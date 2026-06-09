# M-II Operational Audit

Self-contained HTML wizard that guides a small or mid-size business owner through M-II Operations'
100-touchpoint operational audit, then generates a branded PDF report and forwards results to
[Randy.Derrick@miiops.com](mailto:Randy.Derrick@miiops.com) for a 30-minute review call.

**Live entry point:** open `operational-audit-wizard.html` in any modern browser, or host it at a public URL
(Hostinger, GitHub Pages, Railway static, etc.).

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
6. **Submit** — generates a branded PDF (cover · executive summary · impact areas · prioritized action
   plan · full response log · next-steps page), downloads it to the customer's device, and emails the
   results + PDF attachment to Randy with the subject **"Operational Audit — [Company Name]"**.

---

## Configure before going live

Open `operational-audit-wizard.html` in a text editor and find the **CONFIG** section near the top of the
`<script>` block.

### 1. Web3Forms (email delivery)

```js
const WEB3FORMS_KEY = "REPLACE_WITH_YOUR_WEB3FORMS_ACCESS_KEY";
```

Go to <https://web3forms.com>, enter `Randy.Derrick@miiops.com`, and Web3Forms will email you a free
access key (no signup, no backend). Paste it between the quotes.

Until this is configured, submission falls back to a pre-filled `mailto:` link so the customer can send
the results manually.

### 2. Stripe Payment Link

```js
const STRIPE_PAYMENT_LINK = "REPLACE_WITH_STRIPE_PAYMENT_LINK";
```

1. In Stripe Dashboard → Products → **Payment Links** → create a $998 one-time payment link.
2. Set its **success URL** to the public URL of this page with `?paid=1` appended, e.g.
   `https://miiops.com/operational-audit.html?paid=1`.
3. Paste the Payment Link URL between the quotes.

While the value still starts with `REPLACE_`, the Pay button runs a clearly labeled test simulation so the
rest of the flow can be previewed end-to-end.

---

## Files in this repo

| File | What it is |
| --- | --- |
| `operational-audit-wizard.html` | The standalone wizard. **This is what you host.** |
| `sample_audit_report.pdf` | Example PDF output so you can see what clients receive. |
| `assets/M-II-Operations-Logo-no-background.jpg` | Source logo (embedded as base64 inside the HTML). |
| `assets/M-II_Operations_Audit_Google_Sheets_Template.xlsx` | Original Google Sheets template the question bank was built from. |
| `src/audit_questions.json` | All 100 questions in structured JSON (number, tier, impact, severity). |
| `src/build.py` | Python build script that bakes the logo + questions into the HTML. Re-run it if the question bank ever changes. |

---

## Re-building after editing questions

```bash
# Edit src/audit_questions.json or src/build.py, then:
python3 src/build.py
# This regenerates operational-audit-wizard.html in place.
```

The build script reads `src/audit_questions.json` and `assets/M-II-Operations-Logo-no-background.jpg`,
base64-encodes the logo, and stamps the questions into the HTML template.

---

## Tech notes

- **No backend required.** PDF generation runs client-side via jsPDF. Email goes through Web3Forms.
  Payment goes through a Stripe Payment Link.
- **Fonts:** DM Sans (headings) + Inter (body), loaded from Google Fonts with system sans-serif fallback.
- **Branding:** Navy `#16263F` + gold/silver accent. Matches the M-II Operations logo.
- **Data persistence:** Customer answers are stored in `localStorage` under `mii_audit_v1` and cleared on
  "Clear & Restart" or after a successful submit + new audit.
- **Privacy:** Nothing is sent anywhere until the customer clicks **Generate Report & Send** on the review
  page. PDF is built and emailed in one step; the customer downloads a copy locally.

---

© M-II Operations, LLC · Waxahachie, Texas
