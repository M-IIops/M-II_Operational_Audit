#!/usr/bin/env node
/**
 * M-II Operational Audit — Express server.
 *
 * Responsibilities:
 *   - Serve the wizard from /public.
 *   - Accept anonymous audit submissions at POST /api/submit.
 *     Payload is split atomically into two tables:
 *       audit_responses  (anonymized, for aggregate reporting)
 *       audit_contacts   (PII, linked by anon_id)
 *   - Provide an admin dashboard at /admin (Basic Auth).
 *   - Expose aggregate stats at /admin/api/stats (Basic Auth).
 *
 * Environment variables:
 *   PORT          (Railway sets this automatically; default 3000)
 *   DATABASE_URL  (Railway Postgres plugin sets this automatically)
 *   ADMIN_USER    (default: admin)
 *   ADMIN_PASS    (required to access /admin; if unset, /admin returns 503)
 */

const path = require('path');
const express = require('express');
const { Pool } = require('pg');

const crypto = require('crypto');

const PORT = parseInt(process.env.PORT, 10) || 3000;
const DATABASE_URL = process.env.DATABASE_URL || '';

// Strip whitespace + accidentally-pasted surrounding single/double quotes.
// Railway preserves env-var values literally, so a paste like  "my pass"
// (with the quotes) would otherwise never match what the browser sends.
function cleanEnv(v) {
  if (v == null) return '';
  let s = String(v).trim();
  if (s.length >= 2) {
    const first = s[0], last = s[s.length - 1];
    if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
      s = s.slice(1, -1);
    }
  }
  return s;
}
const ADMIN_USER = cleanEnv(process.env.ADMIN_USER) || 'admin';
const ADMIN_PASS = cleanEnv(process.env.ADMIN_PASS);

const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '512kb' }));

// ---------- Postgres ----------
let pool = null;
if (DATABASE_URL) {
  pool = new Pool({
    connectionString: DATABASE_URL,
    ssl:
      DATABASE_URL.includes('railway') || DATABASE_URL.includes('sslmode=')
        ? { rejectUnauthorized: false }
        : false,
    max: 5,
  });
  pool.on('error', (err) => console.error('[pg] pool error:', err.message));
} else {
  console.warn('[server] DATABASE_URL is not set — /api/submit will respond 503.');
}

// ---------- Helpers ----------
function deriveState(location) {
  if (!location || typeof location !== 'string') return null;
  // Accept "City, ST" or "City, State"
  const parts = location.split(',').map((s) => s.trim()).filter(Boolean);
  if (parts.length < 2) return null;
  let st = parts[parts.length - 1];
  // Strip ZIP if present (e.g., "TX 75165")
  st = st.split(/\s+/)[0];
  if (!st) return null;
  return st.length <= 20 ? st.toUpperCase() : null;
}

function isPlainObject(v) {
  return v && typeof v === 'object' && !Array.isArray(v);
}

function clampPct(n) {
  const x = Number(n);
  if (!Number.isFinite(x)) return null;
  if (x < 0) return 0;
  if (x > 100) return 100;
  return Math.round(x * 100) / 100;
}

// Constant-time string compare that tolerates length differences.
function safeEq(a, b) {
  const ab = Buffer.from(String(a));
  const bb = Buffer.from(String(b));
  if (ab.length !== bb.length) {
    // still consume time so we don't leak length
    crypto.timingSafeEqual(ab, ab);
    return false;
  }
  return crypto.timingSafeEqual(ab, bb);
}

function basicAuth(req, res, next) {
  if (!ADMIN_PASS) {
    return res
      .status(503)
      .send('Admin dashboard disabled. Set ADMIN_PASS env var to enable.');
  }
  const header = req.headers.authorization || '';
  if (!header.startsWith('Basic ')) {
    res.set('WWW-Authenticate', 'Basic realm="M-II Audit Admin", charset="UTF-8"');
    res.set('Cache-Control', 'no-store');
    return res.status(401).send('Authentication required.');
  }
  let decoded = '';
  try {
    decoded = Buffer.from(header.slice(6), 'base64').toString('utf8');
  } catch {
    res.set('WWW-Authenticate', 'Basic realm="M-II Audit Admin", charset="UTF-8"');
    res.set('Cache-Control', 'no-store');
    return res.status(401).send('Invalid credentials.');
  }
  const idx = decoded.indexOf(':');
  const user = idx >= 0 ? decoded.slice(0, idx) : decoded;
  const pass = idx >= 0 ? decoded.slice(idx + 1) : '';
  if (safeEq(user, ADMIN_USER) && safeEq(pass, ADMIN_PASS)) return next();
  console.warn(
    '[admin] auth failed: provided user=%j pass-length=%d; expected user=%j pass-length=%d',
    user, pass.length, ADMIN_USER, ADMIN_PASS.length
  );
  res.set('WWW-Authenticate', 'Basic realm="M-II Audit Admin", charset="UTF-8"');
  res.set('Cache-Control', 'no-store');
  return res.status(401).send('Invalid credentials.');
}

// ---------- Routes ----------
app.get('/healthz', (req, res) => {
  res.json({
    ok: true,
    db: !!pool,
    admin_configured: !!ADMIN_PASS,
    admin_user: ADMIN_USER,
    admin_pass_length: ADMIN_PASS.length,
    time: new Date().toISOString(),
  });
});

/**
 * POST /api/submit
 * Body: {
 *   anon: {
 *     industry, revenue_range, headcount,
 *     overall_pct, tier_pcts, category_pcts, severity_pcts,
 *     answers, total_answered, user_agent
 *   },
 *   contact: {
 *     company, contact_name, email, phone, role, location
 *   }
 * }
 */
app.post('/api/submit', async (req, res) => {
  if (!pool) {
    return res.status(503).json({ ok: false, error: 'storage_unavailable' });
  }
  const body = req.body || {};
  const anon = isPlainObject(body.anon) ? body.anon : {};
  const contact = isPlainObject(body.contact) ? body.contact : {};

  const overall_pct = clampPct(anon.overall_pct);
  const tier_pcts = isPlainObject(anon.tier_pcts) ? anon.tier_pcts : {};
  const category_pcts = isPlainObject(anon.category_pcts) ? anon.category_pcts : {};
  const severity_pcts = isPlainObject(anon.severity_pcts) ? anon.severity_pcts : {};
  const answers = isPlainObject(anon.answers) ? anon.answers : {};
  const total_answered = Number.isFinite(Number(anon.total_answered))
    ? parseInt(anon.total_answered, 10)
    : 0;
  const state = deriveState(contact.location);

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const respRow = await client.query(
      `INSERT INTO audit_responses
        (industry, revenue_range, headcount, state, overall_pct,
         tier_pcts, category_pcts, severity_pcts, answers, total_answered, user_agent)
       VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7::jsonb,$8::jsonb,$9::jsonb,$10,$11)
       RETURNING anon_id`,
      [
        (anon.industry || '').toString().slice(0, 120) || null,
        (anon.revenue_range || '').toString().slice(0, 60) || null,
        (anon.headcount || '').toString().slice(0, 60) || null,
        state,
        overall_pct,
        JSON.stringify(tier_pcts),
        JSON.stringify(category_pcts),
        JSON.stringify(severity_pcts),
        JSON.stringify(answers),
        total_answered,
        (anon.user_agent || req.headers['user-agent'] || '').toString().slice(0, 500),
      ],
    );
    const anonId = respRow.rows[0].anon_id;

    await client.query(
      `INSERT INTO audit_contacts
        (anon_id, company, contact_name, email, phone, role, location, overall_pct)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
      [
        anonId,
        (contact.company || '').toString().slice(0, 200) || null,
        (contact.contact_name || '').toString().slice(0, 200) || null,
        (contact.email || '').toString().slice(0, 200) || null,
        (contact.phone || '').toString().slice(0, 60) || null,
        (contact.role || '').toString().slice(0, 120) || null,
        (contact.location || '').toString().slice(0, 200) || null,
        overall_pct,
      ],
    );

    await client.query('COMMIT');
    res.json({ ok: true, anon_id: anonId });
  } catch (err) {
    await client.query('ROLLBACK').catch(() => {});
    console.error('[submit] error:', err.message);
    res.status(500).json({ ok: false, error: 'insert_failed' });
  } finally {
    client.release();
  }
});

// ---------- Admin ----------
app.get('/admin', basicAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

app.get('/admin/api/stats', basicAuth, async (req, res) => {
  if (!pool) return res.status(503).json({ ok: false, error: 'storage_unavailable' });
  try {
    const [
      totals,
      byIndustry,
      byRevenue,
      byHeadcount,
      byState,
      perDay,
      tierAvg,
      categoryAvg,
      severityAvg,
      mostFailed,
      recentContacts,
    ] = await Promise.all([
      pool.query(`
        SELECT
          COUNT(*)::int                AS total,
          ROUND(AVG(overall_pct)::numeric, 1) AS avg_overall,
          MIN(submitted_at)            AS first_at,
          MAX(submitted_at)            AS last_at
        FROM audit_responses
      `),
      pool.query(`
        SELECT COALESCE(industry,'(unspecified)') AS label,
               COUNT(*)::int AS n,
               ROUND(AVG(overall_pct)::numeric, 1) AS avg_pct
        FROM audit_responses
        GROUP BY 1
        ORDER BY n DESC
        LIMIT 20
      `),
      pool.query(`
        SELECT COALESCE(revenue_range,'(unspecified)') AS label,
               COUNT(*)::int AS n,
               ROUND(AVG(overall_pct)::numeric, 1) AS avg_pct
        FROM audit_responses
        GROUP BY 1
        ORDER BY n DESC
      `),
      pool.query(`
        SELECT COALESCE(headcount,'(unspecified)') AS label,
               COUNT(*)::int AS n,
               ROUND(AVG(overall_pct)::numeric, 1) AS avg_pct
        FROM audit_responses
        GROUP BY 1
        ORDER BY n DESC
      `),
      pool.query(`
        SELECT COALESCE(state,'(unknown)') AS label,
               COUNT(*)::int AS n
        FROM audit_responses
        GROUP BY 1
        ORDER BY n DESC
        LIMIT 25
      `),
      pool.query(`
        SELECT date_trunc('day', submitted_at) AS day,
               COUNT(*)::int AS n
        FROM audit_responses
        WHERE submitted_at > NOW() - INTERVAL '90 days'
        GROUP BY 1
        ORDER BY 1
      `),
      pool.query(`
        SELECT
          ROUND(AVG((tier_pcts->>'Foundations')::numeric), 1)     AS foundations,
          ROUND(AVG((tier_pcts->>'Implementation')::numeric), 1)  AS implementation,
          ROUND(AVG((tier_pcts->>'Transformation')::numeric), 1)  AS transformation
        FROM audit_responses
      `),
      pool.query(`
        WITH keys AS (
          SELECT DISTINCT jsonb_object_keys(category_pcts) AS k FROM audit_responses
        )
        SELECT k AS label,
               ROUND(AVG((r.category_pcts->>k)::numeric), 1) AS avg_pct,
               COUNT(*)::int AS n
        FROM keys, audit_responses r
        WHERE r.category_pcts ? k
        GROUP BY k
        ORDER BY avg_pct ASC NULLS LAST
      `),
      pool.query(`
        WITH keys AS (
          SELECT DISTINCT jsonb_object_keys(severity_pcts) AS k FROM audit_responses
        )
        SELECT k AS label,
               ROUND(AVG((r.severity_pcts->>k)::numeric), 1) AS avg_pct,
               COUNT(*)::int AS n
        FROM keys, audit_responses r
        WHERE r.severity_pcts ? k
        GROUP BY k
        ORDER BY avg_pct ASC NULLS LAST
      `),
      pool.query(`
        WITH expanded AS (
          SELECT key AS qid, (value)::text::int AS score
          FROM audit_responses, jsonb_each(answers)
        )
        SELECT qid,
               COUNT(*) FILTER (WHERE score = 0)::int AS zero_count,
               COUNT(*) FILTER (WHERE score = 1)::int AS one_count,
               COUNT(*) FILTER (WHERE score = 2)::int AS two_count,
               COUNT(*)::int AS total,
               ROUND(AVG(score)::numeric, 2) AS avg_score
        FROM expanded
        GROUP BY qid
        ORDER BY avg_score ASC NULLS LAST, zero_count DESC
        LIMIT 25
      `),
      pool.query(`
        SELECT submitted_at, company, contact_name, email, role, location, overall_pct
        FROM audit_contacts
        ORDER BY submitted_at DESC
        LIMIT 25
      `),
    ]);

    res.json({
      ok: true,
      totals: totals.rows[0],
      by_industry: byIndustry.rows,
      by_revenue: byRevenue.rows,
      by_headcount: byHeadcount.rows,
      by_state: byState.rows,
      per_day: perDay.rows,
      tier_avg: tierAvg.rows[0],
      category_avg: categoryAvg.rows,
      severity_avg: severityAvg.rows,
      most_failed: mostFailed.rows,
      recent_contacts: recentContacts.rows,
    });
  } catch (err) {
    console.error('[stats] error:', err.message);
    res.status(500).json({ ok: false, error: 'stats_failed', detail: err.message });
  }
});

// ---------- Static wizard ----------
app.use(express.static(path.join(__dirname, 'public'), { extensions: ['html'] }));

// Fallback to wizard for unknown GETs (single-page friendly)
app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api') || req.path.startsWith('/admin')) return next();
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`[server] M-II Audit listening on :${PORT}`);
});
