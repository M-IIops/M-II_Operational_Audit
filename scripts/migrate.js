#!/usr/bin/env node
/**
 * Idempotent Postgres migration for the M-II Operational Audit.
 * Runs at deploy time (see railway.json startCommand).
 *
 * Tables:
 *   audit_responses  - anonymized data for aggregate reporting
 *   audit_contacts   - PII linked to a response via anon_id, kept separate
 */
const { Pool } = require('pg');

const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error('[migrate] DATABASE_URL is not set; skipping migration.');
  console.error('[migrate] Add a Postgres service to your Railway project and connect it.');
  process.exit(0); // exit 0 so the deploy continues serving the static wizard
}

const pool = new Pool({
  connectionString: DATABASE_URL,
  ssl: DATABASE_URL.includes('railway') || DATABASE_URL.includes('sslmode=')
    ? { rejectUnauthorized: false }
    : false,
});

const SQL = `
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS audit_responses (
  anon_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  submitted_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  industry         TEXT,
  revenue_range    TEXT,
  headcount        TEXT,
  state            TEXT,           -- US state only, derived from contact.location
  overall_pct      NUMERIC(5,2),   -- 0.00 - 100.00
  tier_pcts        JSONB NOT NULL DEFAULT '{}'::jsonb,
  category_pcts    JSONB NOT NULL DEFAULT '{}'::jsonb,
  severity_pcts    JSONB NOT NULL DEFAULT '{}'::jsonb,
  answers          JSONB NOT NULL DEFAULT '{}'::jsonb,  -- {"1":0,"2":1,...}
  total_answered   INTEGER NOT NULL DEFAULT 0,
  user_agent       TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_responses_submitted_at ON audit_responses(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_responses_industry     ON audit_responses(industry);
CREATE INDEX IF NOT EXISTS idx_audit_responses_revenue      ON audit_responses(revenue_range);

CREATE TABLE IF NOT EXISTS audit_contacts (
  anon_id          UUID PRIMARY KEY REFERENCES audit_responses(anon_id) ON DELETE CASCADE,
  submitted_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  company          TEXT,
  contact_name     TEXT,
  email            TEXT,
  phone            TEXT,
  role             TEXT,
  location         TEXT,           -- full "City, State" as entered
  overall_pct      NUMERIC(5,2)
);

CREATE INDEX IF NOT EXISTS idx_audit_contacts_email        ON audit_contacts(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_audit_contacts_submitted_at ON audit_contacts(submitted_at DESC);
`;

(async () => {
  try {
    await pool.query(SQL);
    console.log('[migrate] OK - schema is up to date.');
  } catch (err) {
    console.error('[migrate] ERROR:', err.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
})();
