# M-II Operational Audit

Self-contained HTML wizard that guides a small or mid-size business owner through M-II Operations'
100-touchpoint operational audit, then generates a branded PDF report and forwards results to
[Randy.Derrick@miiops.com](mailto:Randy.Derrick@miiops.com) for a 30-minute review call.

Every submission is also stored anonymously in a Postgres database so M-II can run aggregate
reports on the most commonly neglected areas (policies, authority matrix, onboarding, etc.).
Contact information is stored in a separate table linked only by a random UUID — the response
data and the contact data are never joined in any of the admin dashboard reports.

---

## What it does

1. **Intro page** — pitches the $998 audit and the 30-minute review call.
2. **Stripe payment step** — redirects to a Stripe Payment Link. On successful payment, Stripe returns the
   customer to this page with `?paid=1`, which unlocks the questionnaire.
3. **Contact & company form** — captures the fields needed to brand the report and schedule the call.
4. **100 questions in 3 tiers** — Foundations (1–30), Implementation (31–65), Transformation (66–100).
   Each question is scored 0 / 1 / 2 ("Not in place" / "Partial" / "Fully in place") and tagged with an
   impact area (Productivity, Margin, Founder Freedom, Compliance, Growth) and a risk severity (High,
   Medium, Low). Answers are saved to `localStorage` so save-and-resume just works.
5. **Review page** — color-coded score grid, overall maturity %, per-tier interpretation.
6. **Submit** —
   - Generates a branded PDF (cover · executive summary · impact areas · prioritized action plan ·
     full response log · next-steps page) and downloads it to the customer's device.
   - Emails the results + PDF attachment to Randy with the subject **"Operational Audit — [Company Name]"**.
   - Stores the anonymized score breakdown in Postgres (`audit_responses`) and the contact info in
     a separate table (`audit_contacts`) linked only by a random `anon_id` UUID.
7. **Admin dashboard at `/admin`** — Basic-Auth-protected page showing total submissions, average
   maturity, weakest tier and impact area, most-neglected questions, distribution by industry /
   revenue / headcount / state, and the most recent 25 contacts.

---

## Deploy to Railway

This repo deploys as an Express app on Railway with a Postgres add-on.

1. In Railway, click **+ New → Deploy from GitHub repo → `M-IIops/M-II_Operational_Audit`**.
   *(If the repo doesn't appear, go to <https://github.com/settings/installations>, find Railway,
   click Configure on the **M-IIops** org installation, and grant access to this repo.)*
2. Railway detects `package.json` and `railway.json` and builds automatically (Nixpacks → Node).
3. **Add a Postgres service:** in the same Railway project, click **+ New → Database → Add PostgreSQL**.
   Railway will inject `DATABASE_URL` into the Express service automatically. On the next deploy
   the migration script creates the `audit_responses` and `audit_contacts` tables.
4. **Set environment variables** on the Express service (Service → Variables):
   - `ADMIN_USER` — username for `/admin` (default: `admin`)
   - `ADMIN_PASS` — **required** to enable the admin dashboard. If unset, `/admin` returns 503.
   - `WEB3FORMS_KEY` is currently configured inside `public/index.html` (see below); it does **not**
     need to be set as an env var.
5. Once deployed, click **Settings → Networking → Generate Domain** to get a public URL.
   This deployment is live at **<https://m-iioperationalaudit-production.up.railway.app>**.
   Add a custom domain (e.g. `audit.miiops.com`) later if you'd like a branded URL.
6. Set your Stripe Payment Link's **success URL** to:
   `https://m-iioperationalaudit-production.up.railway.app/welcome`
   This shows the customer a branded thank-you page with a "Start the Audit"
   button that forwards them into the wizard with `?paid=1`.

Files that make this work:
- `package.json` — declares `express` and `pg` and exposes `npm start` on `$PORT`.
- `railway.json` — start command runs the migration then boots the server:
  `node scripts/migrate.js && node server.js`.
- `scripts/migrate.js` — idempotent Postgres schema setup. Safe to run on every deploy.
- `server.js` — Express app: serves `public/`, exposes `POST /api/submit`, `/admin`, and
  `/admin/api/stats`.

The migration script exits cleanly (status 0) if `DATABASE_URL` is not set, so the static wizard
still serves even before you attach Postgres.

---

## Configure before going live

Open `public/index.html` in a text editor and find the **CONFIG** section near the top of the
`<script>` block.

### 1. Web3Forms (email delivery)

```js
const WEB3FORMS_KEY = "REPLACE_WITH_YOUR_WEB3FORMS_ACCESS_KEY";
```

Go to <https://web3forms.com>, enter `Randy.Derrick@miiops.com`, and Web3Forms will email you a free
access key (no signup, no backend). Paste it between the quotes.

Until this is configured, submission falls back to a pre-filled `mailto:` link so the customer can send
the results manually. The anonymized record is still saved to Postgres regardless of email status.

### 2. Stripe Payment Link

```js
const STRIPE_PAYMENT_LINK = "REPLACE_WITH_STRIPE_PAYMENT_LINK";
```

1. In Stripe Dashboard → Products → **Payment Links** → create a $998 one-time payment link.
2. Set its **success URL** to the branded welcome page:
   `https://m-iioperationalaudit-production.up.railway.app/welcome`
   That page thanks the customer, lays out the three-step flow, and has a button that
   forwards them into the wizard with `?paid=1`. (You can also point the success URL
   directly at `/?paid=1` to skip the welcome page, but the welcome page makes for a
   much smoother handoff.)
3. Paste the Payment Link URL between the quotes.

While the value still starts with `REPLACE_`, the Pay button runs a clearly labeled test simulation so the
rest of the flow can be previewed end-to-end.

### 3. Admin dashboard credentials (env vars)

Set in Railway → Service → Variables:

```
ADMIN_USER = admin
ADMIN_PASS = <pick a strong password>
```

Visit <https://m-iioperationalaudit-production.up.railway.app/admin> and the browser
will prompt for these credentials (HTTP Basic Auth).

---

## Privacy model

The audit's storage is intentionally split into two tables:

| Table | Contains | Used in admin dashboard? |
| --- | --- | --- |
| `audit_responses` | Anonymized score breakdown (industry, revenue range, headcount, state, per-tier %, per-impact-area %, per-severity %, individual question scores 0/1/2, total answered, user-agent). Keyed by a random UUID `anon_id`. | **Yes — this powers all aggregate reports.** |
| `audit_contacts` | Company name, contact name, email, phone, role, full location. Keyed by the same `anon_id` as a foreign key. | Only the "recent contacts" table shows raw entries; aggregate charts never join contacts in. |

If you ever need to forget a customer, deleting their row in `audit_responses` cascades and removes
their `audit_contacts` row too.

---

## Files in this repo

| File | What it is |
| --- | --- |
| `public/index.html` | The standalone wizard. Served at `/`. |
| `public/welcome.html` | Post-payment landing page. Served at `/welcome`. Stripe's Payment Link success URL points here. |
| `public/admin.html` | The admin dashboard (charts + tables). Served at `/admin` behind Basic Auth. |
| `public/sample_audit_report.pdf` | Example PDF output so you can see what clients receive. |
| `server.js` | Express app: static `/public`, `POST /api/submit`, `/admin`, `/admin/api/stats`. |
| `scripts/migrate.js` | Postgres schema migration (idempotent). |
| `package.json` | Declares Express + pg dependencies and the `start` script. |
| `railway.json` | Railway build/start configuration (migrate then server). |
| `assets/M-II-Operations-Logo-no-background.jpg` | Source logo (embedded as base64 inside the HTML). |
| `assets/M-II_Operations_Audit_Google_Sheets_Template.xlsx` | Original Google Sheets template the question bank was built from. |
| `src/audit_questions.json` | All 100 questions in structured JSON (number, tier, impact, severity). |
| `src/build.py` | Python build script that bakes the logo + questions into the HTML. Re-run it if the question bank ever changes. |

---

## Re-building after editing questions

```bash
# Edit src/audit_questions.json or src/build.py, then:
python3 src/build.py
# This regenerates public/index.html in place.
```

The build script reads `src/audit_questions.json` and `assets/M-II-Operations-Logo-no-background.jpg`,
base64-encodes the logo, and stamps the questions into the HTML template.

---

## Local development

```bash
# Install dependencies
npm install

# Run a local Postgres (or set DATABASE_URL to any existing Postgres)
export DATABASE_URL="postgres://user:pass@localhost:5432/mii_audit"
export ADMIN_USER=admin
export ADMIN_PASS=changeme
export PORT=3000

# Apply schema and start
npm run migrate
npm start
```

Then visit:
- `http://localhost:3000/` — the wizard
- `http://localhost:3000/admin` — the admin dashboard (Basic Auth)
- `http://localhost:3000/healthz` — health check (also reports whether DB is wired up)

---

## Tech notes

- **Express + Postgres backend.** PDF generation still runs client-side via jsPDF (no server-side
  rendering). Email goes through Web3Forms. Payment goes through a Stripe Payment Link.
- **Fonts:** DM Sans (headings) + Inter (body), loaded from Google Fonts with system sans-serif fallback.
- **Branding:** Navy `#16263F` + gold/silver accent. Matches the M-II Operations logo.
- **Data persistence:** Customer answers are stored in `localStorage` under `mii_audit_v1` and cleared on
  "Clear & Restart" or after a successful submit + new audit. They're also written to Postgres at submit.
- **Resilience:** The `POST /api/submit` call is best-effort — if Postgres is unreachable, the email
  and PDF flow still complete normally. The migration script is idempotent and won't fail on re-runs.

---

© M-II Operations, LLC · Waxahachie, Texas
