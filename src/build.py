"""
Build script for the M-II Operational Audit wizard.

Reads:
    ../assets/M-II-Operations-Logo-no-background.jpg
    ./audit_questions.json

Writes:
    ../operational-audit-wizard.html

Usage (from anywhere):
    python3 src/build.py
"""
import base64
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(ROOT, 'assets', 'M-II-Operations-Logo-no-background.jpg')
QUESTIONS_PATH = os.path.join(ROOT, 'src', 'audit_questions.json')
OUTPUT_PATH = os.path.join(ROOT, 'operational-audit-wizard.html')

with open(LOGO_PATH, 'rb') as f:
    logo_b64 = base64.b64encode(f.read()).decode('ascii')

with open(QUESTIONS_PATH) as f:
    questions = json.load(f)

questions_min = json.dumps(questions, separators=(',', ':'))

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Operational Audit — M-II Operations</title>
<meta name="theme-color" content="#16263F" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
:root{
  --navy:#16263F;
  --navy-2:#1F3354;
  --navy-deep:#0E1A2D;
  --silver:#A8B0BC;
  --silver-2:#C9CFD9;
  --ink:#1A1F2B;
  --ink-2:#4A5160;
  --ink-3:#7A8093;
  --bg:#F6F7F9;
  --surface:#FFFFFF;
  --border:#E2E5EB;
  --accent:#C9A24B;
  --accent-2:#8E6F26;
  --success:#2F7D4F;
  --error:#A12C42;
  --radius:10px;
  --radius-lg:14px;
  --shadow-sm:0 1px 2px rgba(14,26,45,.05),0 1px 1px rgba(14,26,45,.03);
  --shadow:0 4px 14px rgba(14,26,45,.08),0 1px 3px rgba(14,26,45,.04);
  --shadow-lg:0 12px 32px rgba(14,26,45,.12);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);font-family:'Inter',system-ui,-apple-system,Segoe UI,sans-serif;font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;text-rendering:optimizeLegibility}
h1,h2,h3,h4{font-family:'DM Sans','Inter',system-ui,sans-serif;font-weight:600;letter-spacing:-0.015em;color:var(--navy);margin:0 0 .5em}
h1{font-size:clamp(28px,4.2vw,42px);line-height:1.15;letter-spacing:-0.02em;font-weight:700}
h2{font-size:clamp(22px,2.6vw,28px);line-height:1.25;font-weight:600}
h3{font-size:18px;line-height:1.35;font-weight:600}
p{margin:0 0 1em;color:var(--ink-2)}
a{color:var(--navy);text-decoration:underline;text-decoration-color:var(--silver-2);text-underline-offset:2px}
a:hover{text-decoration-color:var(--accent)}
.container{max-width:920px;margin:0 auto;padding:0 24px}

/* Header */
.site-header{background:var(--navy);color:#fff;border-bottom:3px solid var(--accent)}
.site-header .container{display:flex;align-items:center;justify-content:space-between;padding-top:18px;padding-bottom:18px;gap:16px}
.brand{display:flex;align-items:center;gap:12px}
.brand img{height:46px;width:auto;display:block}
.brand-text{font-family:'DM Sans',sans-serif;font-weight:700;font-size:15px;letter-spacing:.04em;text-transform:uppercase;color:#fff;line-height:1}
.brand-text span{display:block;font-weight:500;font-size:11px;color:var(--silver-2);letter-spacing:.18em;margin-top:4px}
.header-meta{font-size:13px;color:var(--silver-2);text-align:right}
.header-meta strong{color:#fff;display:block;font-weight:600;font-size:14px}

/* Layout */
main{padding:40px 0 80px;min-height:calc(100vh - 96px)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);box-shadow:var(--shadow);padding:36px}
@media(max-width:640px){.card{padding:24px 20px}}

/* Buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font-family:'Inter',sans-serif;font-weight:600;font-size:15px;letter-spacing:-0.005em;padding:12px 22px;border-radius:8px;border:1px solid transparent;cursor:pointer;transition:all .15s ease;text-decoration:none;line-height:1;min-height:44px}
.btn-primary{background:var(--navy);color:#fff;border-color:var(--navy)}
.btn-primary:hover{background:var(--navy-2);box-shadow:var(--shadow)}
.btn-primary:disabled{background:var(--silver);border-color:var(--silver);cursor:not-allowed}
.btn-ghost{background:transparent;color:var(--navy);border-color:var(--border)}
.btn-ghost:hover{background:var(--bg);border-color:var(--silver-2)}
.btn-accent{background:var(--accent);color:var(--navy-deep);border-color:var(--accent-2);font-weight:700}
.btn-accent:hover{background:var(--accent-2);color:#fff}
.btn-lg{padding:16px 32px;font-size:17px;min-height:54px}

/* Forms */
.field{margin-bottom:20px}
.field label{display:block;font-size:13px;font-weight:600;color:var(--navy);margin-bottom:6px;letter-spacing:.01em}
.field .hint{font-size:12px;color:var(--ink-3);margin-top:4px}
.field input,.field select,.field textarea{width:100%;padding:11px 14px;border:1px solid var(--border);border-radius:8px;font-family:inherit;font-size:15px;color:var(--ink);background:var(--surface);transition:border-color .12s,box-shadow .12s}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--navy);box-shadow:0 0 0 3px rgba(22,38,63,.12)}
.field-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:640px){.field-grid{grid-template-columns:1fr}}
.required{color:var(--error)}

/* Progress */
.progress{margin-bottom:28px}
.progress-meta{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;font-size:13px;color:var(--ink-3)}
.progress-meta strong{color:var(--navy);font-weight:600;font-size:14px}
.progress-bar{height:6px;background:var(--border);border-radius:99px;overflow:hidden}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--navy) 0%,var(--navy-2) 100%);border-radius:99px;transition:width .35s ease;width:0%}
.tier-badge{display:inline-block;padding:4px 10px;background:var(--navy);color:#fff;border-radius:99px;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:14px}

/* Question card */
.q-list{display:flex;flex-direction:column;gap:14px;margin-bottom:28px}
.q-item{border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;background:var(--surface);transition:border-color .12s,box-shadow .12s}
.q-item:hover{border-color:var(--silver-2)}
.q-item.answered{border-color:var(--navy);background:#FBFCFD}
.q-head{display:flex;gap:14px;align-items:flex-start;margin-bottom:12px}
.q-num{flex-shrink:0;width:30px;height:30px;background:var(--bg);border:1px solid var(--border);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:var(--ink-2);font-variant-numeric:tabular-nums}
.q-item.answered .q-num{background:var(--navy);color:#fff;border-color:var(--navy)}
.q-text{flex:1;font-size:15px;font-weight:500;color:var(--ink);line-height:1.45}
.q-tags{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
.q-tag{font-size:10px;font-weight:600;padding:2px 8px;border-radius:99px;letter-spacing:.05em;text-transform:uppercase;background:var(--bg);color:var(--ink-3);border:1px solid var(--border)}
.q-tag.sev-High{background:#FDEAEE;color:#8B1E33;border-color:#F5C7D0}
.q-tag.sev-Medium{background:#FFF5E1;color:#7A5A12;border-color:#F0DCAA}
.q-tag.sev-Low{background:#E8F0E8;color:#2F5C36;border-color:#C5DAC7}
.q-options{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-left:44px}
@media(max-width:640px){.q-options{grid-template-columns:1fr;margin-left:0}}
.q-opt{position:relative;cursor:pointer}
.q-opt input{position:absolute;opacity:0;pointer-events:none}
.q-opt-label{display:block;padding:10px 14px;border:1px solid var(--border);border-radius:8px;font-size:13px;font-weight:500;color:var(--ink-2);text-align:center;transition:all .12s ease;background:var(--surface)}
.q-opt:hover .q-opt-label{border-color:var(--silver);color:var(--ink)}
.q-opt input:checked + .q-opt-label{background:var(--navy);color:#fff;border-color:var(--navy);font-weight:600}
.q-opt input:focus-visible + .q-opt-label{box-shadow:0 0 0 3px rgba(22,38,63,.18)}

/* Nav buttons */
.nav-row{display:flex;justify-content:space-between;gap:12px;padding-top:24px;border-top:1px solid var(--border);margin-top:8px}
.nav-row .spacer{flex:1}

/* Steps indicator */
.steps{display:flex;gap:6px;margin-bottom:24px;flex-wrap:wrap}
.step-dot{flex:1;min-width:60px;height:4px;background:var(--border);border-radius:99px;transition:background .25s}
.step-dot.done{background:var(--navy)}
.step-dot.current{background:var(--accent)}

/* Hero / intro */
.hero{text-align:center;padding:24px 0 8px}
.hero .eyebrow{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-3);margin-bottom:14px}
.hero h1{margin-bottom:14px}
.hero .lead{font-size:18px;color:var(--ink-2);max-width:640px;margin:0 auto 32px;line-height:1.55}
.feature-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:32px 0}
@media(max-width:640px){.feature-grid{grid-template-columns:1fr}}
.feature{padding:18px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg);text-align:left}
.feature h3{font-size:14px;margin-bottom:4px;color:var(--navy)}
.feature p{font-size:13px;margin:0;color:var(--ink-2)}
.price-box{background:var(--navy);color:#fff;border-radius:var(--radius-lg);padding:28px;text-align:center;margin:32px 0}
.price-box .price{font-family:'DM Sans',sans-serif;font-size:48px;font-weight:700;line-height:1;letter-spacing:-0.025em;margin:8px 0}
.price-box .price small{font-size:24px;font-weight:500;color:var(--silver-2);letter-spacing:0}
.price-box .price-meta{font-size:13px;color:var(--silver-2);margin-top:8px}

/* Review */
.review-section{margin-bottom:32px}
.review-section h3{display:flex;justify-content:space-between;align-items:baseline;padding-bottom:8px;border-bottom:1px solid var(--border);margin-bottom:12px}
.review-section h3 .pct{font-family:'DM Sans',sans-serif;font-size:20px;color:var(--navy);font-weight:700}
.review-list{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;font-size:12px}
@media(max-width:640px){.review-list{grid-template-columns:repeat(2,1fr)}}
.review-list .ri{padding:4px 8px;border-radius:6px;background:var(--bg);display:flex;justify-content:space-between;gap:8px}
.review-list .ri.score-0{background:#FDEAEE;color:#8B1E33}
.review-list .ri.score-1{background:#FFF5E1;color:#7A5A12}
.review-list .ri.score-2{background:#E8F0E8;color:#2F5C36}
.review-list .ri.score--{background:#F0F0F2;color:var(--ink-3)}
.review-list .ri-n{font-weight:700;font-variant-numeric:tabular-nums}

.alert{padding:14px 18px;border-radius:var(--radius);margin-bottom:20px;font-size:14px;display:flex;gap:12px;align-items:flex-start}
.alert-warn{background:#FFF5E1;border:1px solid #F0DCAA;color:#7A5A12}
.alert-info{background:#EAF1FB;border:1px solid #C7D9F2;color:#1F3354}
.alert-success{background:#E8F0E8;border:1px solid #C5DAC7;color:#2F5C36}
.alert-error{background:#FDEAEE;border:1px solid #F5C7D0;color:#8B1E33}
.alert strong{font-weight:700}

.footer{padding:32px 0;text-align:center;font-size:12px;color:var(--ink-3);border-top:1px solid var(--border);background:var(--surface);margin-top:48px}

/* Loading spinner */
.spinner{display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

.hidden{display:none !important}

/* Section divider header on question pages */
.section-head{margin-bottom:24px}
.section-head .tier-badge{margin-bottom:10px}
.section-head h2{margin-bottom:6px}
.section-head p{font-size:14px;color:var(--ink-3);margin:0}
</style>
</head>
<body>
<header class="site-header">
  <div class="container">
    <div class="brand">
      <img src="data:image/jpeg;base64,__LOGO_B64__" alt="M-II Operations" />
      <div class="brand-text">M-II Operations<span>Fractional COO · Waxahachie, TX</span></div>
    </div>
    <div class="header-meta">
      <strong>Operational Audit</strong>
      100 touchpoints · 8 areas
    </div>
  </div>
</header>

<main>
  <div class="container">
    <!-- STEP 0: Intro -->
    <section id="step-intro" class="step-panel">
      <div class="card">
        <div class="hero">
          <div class="eyebrow">M-II Operational Audit</div>
          <h1>Find out what your operation actually looks like.</h1>
          <p class="lead">100 touchpoints. Eight focus areas. A branded PDF report you can act on Monday morning — plus a 30-minute review call with Randy.</p>
        </div>

        <div class="feature-grid">
          <div class="feature"><h3>Documentation &amp; SOPs</h3><p>How much runs on written process vs. tribal knowledge.</p></div>
          <div class="feature"><h3>Authority &amp; Org Clarity</h3><p>Who can decide what — and is it written down.</p></div>
          <div class="feature"><h3>Bottlenecks &amp; Productivity</h3><p>Where work piles up and why it stalls.</p></div>
          <div class="feature"><h3>Profit Margin &amp; Compliance</h3><p>Where margin leaks and where risk hides.</p></div>
        </div>

        <div class="price-box">
          <div style="font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--silver-2);font-weight:600">Investment</div>
          <div class="price"><small>$</small>998</div>
          <div class="price-meta">One-time. Includes 30-minute review call with Randy.</div>
        </div>

        <div class="alert alert-info">
          <div><strong>Estimated time:</strong> 35–45 minutes. Save-and-resume works automatically — your answers are stored in this browser until you submit.</div>
        </div>

        <div style="text-align:center;margin-top:28px">
          <button class="btn btn-primary btn-lg" onclick="goTo('payment')">Start the Audit →</button>
        </div>
      </div>
    </section>

    <!-- STEP 0.5: Payment -->
    <section id="step-payment" class="step-panel hidden">
      <div class="card">
        <div class="progress">
          <div class="progress-meta"><span>Secure checkout</span><strong>Payment</strong></div>
          <div class="progress-bar"><div class="progress-fill" style="width:5%"></div></div>
        </div>

        <div class="hero" style="padding-top:0">
          <div class="eyebrow">Step 1 · Secure your audit</div>
          <h2 style="font-size:clamp(24px,3vw,32px);margin-bottom:10px">Confirm your investment</h2>
          <p class="lead" style="font-size:16px;max-width:560px;margin-bottom:24px">One-time payment. Includes the full 100-touchpoint audit, your branded PDF report, and a 30-minute review call with Randy.</p>
        </div>

        <div class="price-box">
          <div style="font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--silver-2);font-weight:600">Operational Audit</div>
          <div class="price"><small>$</small>998</div>
          <div class="price-meta">USD · one-time · secured by Stripe</div>
        </div>

        <div id="payment-mode-banner"></div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:24px 0;font-size:13px;color:var(--ink-2)">
          <div style="display:flex;gap:8px;align-items:flex-start"><span style="color:var(--success);font-weight:700">✓</span><span>100 touchpoints across 8 operational areas</span></div>
          <div style="display:flex;gap:8px;align-items:flex-start"><span style="color:var(--success);font-weight:700">✓</span><span>Custom-branded PDF maturity report</span></div>
          <div style="display:flex;gap:8px;align-items:flex-start"><span style="color:var(--success);font-weight:700">✓</span><span>Prioritized action plan, sorted by risk</span></div>
          <div style="display:flex;gap:8px;align-items:flex-start"><span style="color:var(--success);font-weight:700">✓</span><span>30-minute review call with Randy</span></div>
        </div>

        <div style="text-align:center;margin-top:8px">
          <button id="pay-btn" class="btn btn-accent btn-lg" onclick="startPayment()">Pay $998 with Stripe →</button>
        </div>
        <p style="text-align:center;font-size:12px;color:var(--ink-3);margin-top:14px">After payment you'll return to this page automatically and begin the audit.</p>

        <div class="nav-row" style="margin-top:28px">
          <button type="button" class="btn btn-ghost" onclick="goTo('intro')">← Back</button>
          <div class="spacer"></div>
        </div>
      </div>
    </section>

    <!-- STEP 1: Contact -->
    <section id="step-contact" class="step-panel hidden">
      <div class="card">
        <div class="progress">
          <div class="progress-meta"><span>Step 2 of 6</span><strong>Contact &amp; Company</strong></div>
          <div class="progress-bar"><div class="progress-fill" style="width:15%"></div></div>
        </div>

        <div class="alert alert-success" style="margin-bottom:20px"><div><strong>✓ Payment confirmed.</strong> Let’s get the audit started.</div></div>

        <h2>Tell us about your business</h2>
        <p style="margin-bottom:24px">All fields marked <span class="required">*</span> are required. We use this to personalize your report and schedule your review call.</p>

        <form id="contact-form" onsubmit="event.preventDefault();saveContactAndGo()">
          <div class="field-grid">
            <div class="field">
              <label>Company name <span class="required">*</span></label>
              <input type="text" name="company" required />
            </div>
            <div class="field">
              <label>Primary contact name <span class="required">*</span></label>
              <input type="text" name="name" required />
            </div>
            <div class="field">
              <label>Email <span class="required">*</span></label>
              <input type="email" name="email" required />
            </div>
            <div class="field">
              <label>Phone</label>
              <input type="tel" name="phone" />
            </div>
            <div class="field">
              <label>Role / Title</label>
              <input type="text" name="role" placeholder="Owner, COO, GM…" />
            </div>
            <div class="field">
              <label>Industry</label>
              <input type="text" name="industry" placeholder="Construction, professional services…" />
            </div>
            <div class="field">
              <label>Annual revenue range</label>
              <select name="revenue">
                <option value="">Select…</option>
                <option>Under $1M</option>
                <option>$1M – $3M</option>
                <option>$3M – $5M</option>
                <option>$5M – $10M</option>
                <option>$10M+</option>
              </select>
            </div>
            <div class="field">
              <label>Headcount</label>
              <select name="headcount">
                <option value="">Select…</option>
                <option>Under 10</option>
                <option>10 – 25</option>
                <option>25 – 50</option>
                <option>50 – 75</option>
                <option>75+</option>
              </select>
            </div>
            <div class="field" style="grid-column:1/-1">
              <label>Location (City, State)</label>
              <input type="text" name="location" />
            </div>
          </div>

          <div class="nav-row">
            <button type="button" class="btn btn-ghost" onclick="goTo('intro')">← Back</button>
            <div class="spacer"></div>
            <button type="submit" class="btn btn-primary">Continue →</button>
          </div>
        </form>
      </div>
    </section>

    <!-- STEPS 2-4: Tier questions (rendered dynamically) -->
    <section id="step-tier1" class="step-panel hidden"><div class="card" id="card-tier1"></div></section>
    <section id="step-tier2" class="step-panel hidden"><div class="card" id="card-tier2"></div></section>
    <section id="step-tier3" class="step-panel hidden"><div class="card" id="card-tier3"></div></section>

    <!-- STEP 5: Review & Submit -->
    <section id="step-review" class="step-panel hidden">
      <div class="card">
        <div class="progress">
          <div class="progress-meta"><span>Step 6 of 6</span><strong>Review &amp; Submit</strong></div>
          <div class="progress-bar"><div class="progress-fill" style="width:100%"></div></div>
        </div>

        <h2>Review your results</h2>
        <p style="margin-bottom:24px">Below are your scores by tier. You can go back and change any answer. When you're ready, submit to download your PDF report and send your results to Randy for your review call.</p>

        <div id="review-content"></div>

        <div id="missing-warn" class="alert alert-warn hidden">
          <div><strong>Heads up:</strong> <span id="missing-count">0</span> question(s) are unanswered. They'll score as 0 (not in place) on your report. Go back to update them or continue.</div>
        </div>

        <div class="alert alert-info">
          <div><strong>What happens when you submit:</strong>
          <ol style="margin:8px 0 0 18px;padding:0">
            <li>Your branded PDF report downloads to this device.</li>
            <li>A copy of your results + contact info is emailed to Randy at Randy.Derrick@miiops.com.</li>
            <li>Randy will reach out within one business day to schedule your 30-minute review call.</li>
          </ol>
          </div>
        </div>

        <div id="submit-status"></div>

        <div class="nav-row">
          <button type="button" class="btn btn-ghost" onclick="goTo('tier3')">← Back</button>
          <button type="button" class="btn btn-ghost" onclick="clearAll()">Clear &amp; Restart</button>
          <div class="spacer"></div>
          <button id="submit-btn" type="button" class="btn btn-accent btn-lg" onclick="submitAudit()">Generate Report &amp; Send →</button>
        </div>
      </div>
    </section>

    <!-- DONE -->
    <section id="step-done" class="step-panel hidden">
      <div class="card" style="text-align:center">
        <div style="font-size:48px;line-height:1;margin-bottom:16px">✓</div>
        <h2>Audit complete</h2>
        <p style="font-size:17px;max-width:560px;margin:0 auto 24px">Your PDF report has been downloaded and your results have been sent to Randy. He'll be in touch within one business day to schedule your 30-minute review call.</p>
        <div id="done-detail" class="alert alert-success" style="text-align:left"></div>
        <div style="margin-top:24px">
          <button class="btn btn-primary" onclick="downloadAgain()">Re-download PDF</button>
          <button class="btn btn-ghost" onclick="clearAll()" style="margin-left:8px">Start a New Audit</button>
        </div>
      </div>
    </section>
  </div>
</main>

<footer class="footer">
  <div class="container">
    © <span id="yr"></span> M-II Operations, LLC · Waxahachie, Texas · <a href="mailto:Randy.Derrick@miiops.com">Randy.Derrick@miiops.com</a>
  </div>
</footer>

<script>
document.getElementById('yr').textContent=new Date().getFullYear();

// ============= CONFIG =============
// Web3Forms access key — get free at https://web3forms.com (no signup, no backend needed).
// Replace the placeholder below with your real key, then re-upload this HTML file.
const WEB3FORMS_KEY = "REPLACE_WITH_YOUR_WEB3FORMS_ACCESS_KEY";
const EMAIL_TO = "Randy.Derrick@miiops.com";

// ============= DATA =============
const QUESTIONS = __QUESTIONS_JSON__;
const TIERS = [
  {key:'tier1', name:'Foundations', range:'Questions 1–30', desc:'Documentation, roles, basic structure. The non-negotiables every business needs before it can scale.'},
  {key:'tier2', name:'Implementation', range:'Questions 31–65', desc:'Bottlenecks, productivity, training, meetings. How well current operations actually run.'},
  {key:'tier3', name:'Transformation', range:'Questions 66–100', desc:'Org design, hiring, compliance, founder freedom. What separates an operation from a sellable business.'}
];
const STEP_ORDER = ['intro','payment','contact','tier1','tier2','tier3','review','done'];
const STORAGE_KEY = 'mii_audit_v1';

// ============= STRIPE CONFIG =============
// To enable real Stripe payment:
//   1. In Stripe Dashboard go to Products → Payment Links → create a $998 one-time payment link.
//   2. Set its success URL to the public URL of this page with ?paid=1 appended.
//      Example: https://miiops.com/operational-audit.html?paid=1
//   3. Paste the Payment Link URL between the quotes below (replace the placeholder).
// While the value below starts with "REPLACE_", the Pay button runs a test simulation
// so you can preview the rest of the flow end-to-end.
const STRIPE_PAYMENT_LINK = "REPLACE_WITH_STRIPE_PAYMENT_LINK";
const AUDIT_PRICE_LABEL = "$998";

// ============= STATE =============
let state = loadState();
function loadState(){
  try{ const raw = localStorage.getItem(STORAGE_KEY); if(raw) return JSON.parse(raw); }catch(e){}
  return {contact:{}, answers:{}, currentStep:'intro'};
}
function saveState(){
  try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }catch(e){}
}
function clearAll(){
  if(!confirm('Clear all your answers and start over?')) return;
  localStorage.removeItem(STORAGE_KEY);
  state = {contact:{}, answers:{}, currentStep:'intro'};
  // Reset form fields
  const f = document.getElementById('contact-form'); if(f) f.reset();
  goTo('intro');
}

// ============= RENDER QUESTIONS =============
function tierQuestions(tierName){ return QUESTIONS.filter(q=>q.tier===tierName); }

function renderTierPage(tierIdx){
  const tier = TIERS[tierIdx];
  const qs = tierQuestions(tier.name);
  const container = document.getElementById('card-'+tier.key);
  const stepNum = tierIdx + 3; // payment=1, contact=2, tiers=3,4,5
  const totalAnswered = qs.filter(q => state.answers[q.n] !== undefined).length;
  const overallAnswered = QUESTIONS.filter(q => state.answers[q.n] !== undefined).length;
  const pct = Math.round(((stepNum) / 6) * 100);

  let html = `
    <div class="progress">
      <div class="progress-meta"><span>Step ${stepNum} of 6</span><strong>${overallAnswered} of 100 answered</strong></div>
      <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
    </div>
    <div class="section-head">
      <span class="tier-badge">${tier.name}</span>
      <h2>${tier.name} — ${tier.range}</h2>
      <p>${tier.desc}</p>
    </div>
    <div class="alert alert-info" style="margin-bottom:20px">
      <div><strong>Score each statement:</strong> <em>Not in place</em> (0) · <em>Partially in place</em> (1) · <em>Fully in place</em> (2). Be honest — the report's only useful if the inputs are.</div>
    </div>
    <div class="q-list">
  `;

  qs.forEach(q => {
    const ans = state.answers[q.n];
    const answered = ans !== undefined;
    html += `
      <div class="q-item ${answered?'answered':''}" data-qn="${q.n}">
        <div class="q-head">
          <div class="q-num">${q.n}</div>
          <div style="flex:1">
            <div class="q-text">${escapeHtml(q.q)}</div>
            <div class="q-tags">
              <span class="q-tag">${escapeHtml(q.impact)}</span>
              <span class="q-tag sev-${q.severity}">${escapeHtml(q.severity)} Risk</span>
            </div>
          </div>
        </div>
        <div class="q-options">
          <label class="q-opt">
            <input type="radio" name="q${q.n}" value="0" ${ans===0?'checked':''} onchange="setAnswer(${q.n},0)" />
            <span class="q-opt-label">0 · Not in place</span>
          </label>
          <label class="q-opt">
            <input type="radio" name="q${q.n}" value="1" ${ans===1?'checked':''} onchange="setAnswer(${q.n},1)" />
            <span class="q-opt-label">1 · Partial</span>
          </label>
          <label class="q-opt">
            <input type="radio" name="q${q.n}" value="2" ${ans===2?'checked':''} onchange="setAnswer(${q.n},2)" />
            <span class="q-opt-label">2 · Fully in place</span>
          </label>
        </div>
      </div>
    `;
  });

  html += `</div>`;

  // Tier-section answered counter
  html += `<div style="text-align:center;color:var(--ink-3);font-size:13px;margin-bottom:8px"><span id="tier-count-${tier.key}">${totalAnswered}</span> of ${qs.length} answered in this section</div>`;

  // Nav
  const prev = tierIdx === 0 ? 'contact' : TIERS[tierIdx-1].key;
  const next = tierIdx === 2 ? 'review' : TIERS[tierIdx+1].key;
  html += `
    <div class="nav-row">
      <button type="button" class="btn btn-ghost" onclick="goTo('${prev}')">← Back</button>
      <div class="spacer"></div>
      <button type="button" class="btn btn-primary" onclick="goTo('${next}')">Continue →</button>
    </div>
  `;
  container.innerHTML = html;
}

function setAnswer(qn, val){
  state.answers[qn] = val;
  saveState();
  // toggle the answered class
  const item = document.querySelector(`.q-item[data-qn="${qn}"]`);
  if(item) item.classList.add('answered');
  // update tier counter
  TIERS.forEach(t => {
    const qs = tierQuestions(t.name);
    const answered = qs.filter(q => state.answers[q.n] !== undefined).length;
    const el = document.getElementById('tier-count-'+t.key);
    if(el) el.textContent = answered;
  });
}

function saveContactAndGo(){
  const f = document.getElementById('contact-form');
  const fd = new FormData(f);
  const contact = {};
  fd.forEach((v,k)=>contact[k]=v);
  state.contact = contact;
  saveState();
  goTo('tier1');
}

// ============= PAYMENT =============
function stripeConfigured(){
  return STRIPE_PAYMENT_LINK && !STRIPE_PAYMENT_LINK.startsWith('REPLACE_');
}

function startPayment(){
  if(stripeConfigured()){
    // Real Stripe redirect. Stripe will return user with ?paid=1 (set this as the
    // Payment Link success_url in your Stripe dashboard).
    window.location.href = STRIPE_PAYMENT_LINK;
    return;
  }
  // Test mode — simulate a successful payment so the flow can be previewed.
  const ok = confirm('TEST MODE\n\nNo Stripe Payment Link is configured yet. Simulate a successful payment and continue to the audit?\n\n(Replace STRIPE_PAYMENT_LINK at the top of this file with your real Stripe Payment Link URL to enable live checkout.)');
  if(!ok) return;
  markPaid();
  goTo('contact');
}

function markPaid(){
  state.paid = true;
  state.paidAt = new Date().toISOString();
  saveState();
}

function renderPaymentBanner(){
  const el = document.getElementById('payment-mode-banner');
  if(!el) return;
  if(stripeConfigured()){
    el.innerHTML = '';
  } else {
    el.innerHTML = '<div class="alert alert-warn"><div><strong>Test mode.</strong> No Stripe Payment Link is configured yet. The “Pay” button will simulate a successful payment so you can preview the rest of the flow. To go live, paste your Stripe Payment Link URL into <code>STRIPE_PAYMENT_LINK</code> near the top of this file and set its success URL to this page with <code>?paid=1</code>.</div></div>';
  }
}

// Gate questionnaire steps behind payment
const PAID_STEPS = ['contact','tier1','tier2','tier3','review'];
function enforcePaymentGate(step){
  if(PAID_STEPS.includes(step) && !state.paid){
    return 'payment';
  }
  return step;
}

function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

// ============= NAVIGATION =============
function goTo(step){
  step = enforcePaymentGate(step);
  state.currentStep = step;
  saveState();
  STEP_ORDER.forEach(s => {
    const el = document.getElementById('step-'+s);
    if(el) el.classList.toggle('hidden', s !== step);
  });
  if(step==='payment') renderPaymentBanner();
  if(step==='tier1') renderTierPage(0);
  if(step==='tier2') renderTierPage(1);
  if(step==='tier3') renderTierPage(2);
  if(step==='review') renderReview();
  window.scrollTo({top:0,behavior:'smooth'});
}

// Restore on page load
window.addEventListener('DOMContentLoaded', () => {
  // restore contact form values
  if(state.contact){
    const f = document.getElementById('contact-form');
    Object.entries(state.contact).forEach(([k,v]) => {
      const el = f.elements[k]; if(el) el.value = v;
    });
  }

  // Detect Stripe return: ?paid=1 in the URL means the user just completed checkout.
  const params = new URLSearchParams(window.location.search);
  if(params.get('paid') === '1'){
    markPaid();
    // clean the URL so a refresh doesn't re-trigger
    try { history.replaceState({}, '', window.location.pathname); } catch(e){}
    goTo('contact');
    return;
  }

  // restore step
  const start = state.currentStep && STEP_ORDER.includes(state.currentStep) ? state.currentStep : 'intro';
  // don't drop someone back on the 'done' screen
  goTo(start === 'done' ? 'intro' : start);
});

// ============= SCORING =============
function computeScores(){
  const byTier = {};
  const byCategory = {};
  const bySeverity = {High:{score:0,max:0,answered:0,total:0,missed:[]}, Medium:{score:0,max:0,answered:0,total:0,missed:[]}, Low:{score:0,max:0,answered:0,total:0,missed:[]}};
  let totalScore = 0, totalMax = 0, totalAnswered = 0;
  const gaps = []; // questions scored 0 (full gap)
  const partials = []; // scored 1
  const unanswered = [];

  QUESTIONS.forEach(q => {
    const ans = state.answers[q.n];
    const t = q.tier, c = q.impact, sev = q.severity;
    byTier[t] = byTier[t] || {score:0,max:0,answered:0,total:0};
    byCategory[c] = byCategory[c] || {score:0,max:0,answered:0,total:0};
    byTier[t].total++; byCategory[c].total++; bySeverity[sev].total++; totalMax += 2;
    byTier[t].max += 2; byCategory[c].max += 2; bySeverity[sev].max += 2;
    if(ans !== undefined){
      byTier[t].score += ans; byCategory[c].score += ans; bySeverity[sev].score += ans;
      byTier[t].answered++; byCategory[c].answered++; bySeverity[sev].answered++;
      totalScore += ans; totalAnswered++;
      if(ans === 0) gaps.push(q);
      if(ans === 1) partials.push(q);
    } else {
      unanswered.push(q);
      if(sev === 'High') bySeverity.High.missed.push(q);
    }
  });

  return {byTier, byCategory, bySeverity, totalScore, totalMax, totalAnswered, gaps, partials, unanswered};
}

function interpret(pct){
  if(pct >= 0.85) return {label:'Strong', color:'#2F7D4F', note:'Foundation is solid. Focus on incremental optimization and capturing remaining edge cases.'};
  if(pct >= 0.5)  return {label:'Partial Build', color:'#C9A24B', note:'Core elements exist but coverage is uneven. Targeted reinforcement will yield outsized gains.'};
  return {label:'Significant Opportunity', color:'#A12C42', note:'Material gaps. Prioritized intervention required to reduce founder dependency and operational risk.'};
}

// ============= REVIEW =============
function renderReview(){
  const s = computeScores();
  let html = '';

  // Overall card
  const overallPct = s.totalMax ? s.totalScore / s.totalMax : 0;
  const overall = interpret(overallPct);
  html += `
    <div style="background:var(--navy);color:#fff;border-radius:var(--radius-lg);padding:24px;margin-bottom:24px;display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center">
      <div>
        <div style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--silver-2);font-weight:600;margin-bottom:6px">Overall Maturity</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:34px;font-weight:700;line-height:1;letter-spacing:-0.02em">${(overallPct*100).toFixed(0)}%</div>
        <div style="font-size:13px;color:var(--silver-2);margin-top:6px">${s.totalScore} of ${s.totalMax} possible points · ${s.totalAnswered} of 100 answered</div>
      </div>
      <div style="background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:8px;padding:10px 18px;text-align:center">
        <div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--silver-2)">Tier</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:18px;font-weight:700;margin-top:4px">${overall.label}</div>
      </div>
    </div>
  `;

  // Per tier
  TIERS.forEach(t => {
    const td = s.byTier[t.name] || {score:0,max:0,answered:0,total:0};
    const pct = td.max ? td.score / td.max : 0;
    const interp = interpret(pct);
    html += `
      <div class="review-section">
        <h3>${t.name} <span class="pct" style="color:${interp.color}">${(pct*100).toFixed(0)}% · ${interp.label}</span></h3>
        <div style="font-size:13px;color:var(--ink-3);margin-bottom:10px">${td.score} of ${td.max} pts · ${td.answered} of ${td.total} answered</div>
        <div class="review-list">
    `;
    tierQuestions(t.name).forEach(q => {
      const a = state.answers[q.n];
      const cls = a === undefined ? 'score--' : 'score-'+a;
      const lbl = a === undefined ? '—' : a;
      html += `<div class="ri ${cls}"><span class="ri-n">#${q.n}</span><span>${lbl}</span></div>`;
    });
    html += `</div></div>`;
  });

  document.getElementById('review-content').innerHTML = html;

  if(s.unanswered.length > 0){
    document.getElementById('missing-warn').classList.remove('hidden');
    document.getElementById('missing-count').textContent = s.unanswered.length;
  } else {
    document.getElementById('missing-warn').classList.add('hidden');
  }
}

// ============= PDF GENERATION =============
let lastPdfBlob = null;
let lastPdfFilename = 'M-II_Operational_Audit.pdf';

async function generatePDF(){
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({unit:'pt', format:'letter'});
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const margin = 54;
  const contentW = pageW - margin*2;

  const NAVY = [22,38,63];
  const NAVY_2 = [31,51,84];
  const SILVER = [168,176,188];
  const SILVER_2 = [201,207,217];
  const INK = [26,31,43];
  const INK_2 = [74,81,96];
  const INK_3 = [122,128,147];
  const ACCENT = [201,162,75];
  const RED = [161,44,66];
  const GREEN = [47,125,79];
  const GOLD = [122,90,18];
  const BG = [246,247,249];

  const company = state.contact.company || 'Your Company';
  const name = state.contact.name || '';
  const today = new Date().toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'});
  const s = computeScores();
  const overallPct = s.totalMax ? s.totalScore / s.totalMax : 0;
  const overall = interpret(overallPct);

  // === COVER PAGE ===
  doc.setFillColor(...NAVY);
  doc.rect(0, 0, pageW, pageH, 'F');
  // accent bar
  doc.setFillColor(...ACCENT);
  doc.rect(0, pageH - 8, pageW, 8, 'F');

  // logo (embedded)
  try {
    doc.addImage('data:image/jpeg;base64,__LOGO_B64__', 'JPEG', margin, 80, 140, 74, undefined, 'FAST');
  } catch(e){}

  doc.setTextColor(255,255,255);
  doc.setFont('helvetica','normal');
  doc.setFontSize(10);
  doc.text('M-II OPERATIONS · FRACTIONAL COO', margin, 200);

  doc.setFont('helvetica','bold');
  doc.setFontSize(36);
  doc.text('Operational Audit', margin, 250);
  doc.setFontSize(20);
  doc.setFont('helvetica','normal');
  doc.setTextColor(...SILVER_2);
  doc.text('100-Touchpoint Assessment', margin, 278);

  // Company block
  doc.setDrawColor(...ACCENT);
  doc.setLineWidth(2);
  doc.line(margin, 340, margin + 60, 340);
  doc.setTextColor(...SILVER_2);
  doc.setFontSize(9);
  doc.text('PREPARED FOR', margin, 360);
  doc.setTextColor(255,255,255);
  doc.setFont('helvetica','bold');
  doc.setFontSize(22);
  doc.text(company, margin, 386, {maxWidth: contentW});
  if(name){
    doc.setFont('helvetica','normal');
    doc.setFontSize(13);
    doc.setTextColor(...SILVER_2);
    doc.text(name + (state.contact.role ? ' · ' + state.contact.role : ''), margin, 410);
  }

  // Big score bottom-right
  doc.setFont('helvetica','bold');
  doc.setFontSize(72);
  doc.setTextColor(...ACCENT);
  const pctText = (overallPct*100).toFixed(0) + '%';
  const pctW = doc.getTextWidth(pctText);
  doc.text(pctText, pageW - margin - pctW, pageH - 110);
  doc.setFontSize(12);
  doc.setFont('helvetica','normal');
  doc.setTextColor(255,255,255);
  const lbl = 'Overall Maturity · ' + overall.label;
  const lblW = doc.getTextWidth(lbl);
  doc.text(lbl, pageW - margin - lblW, pageH - 90);

  // Footer cover
  doc.setFontSize(9);
  doc.setTextColor(...SILVER_2);
  doc.text(today, margin, pageH - 40);
  doc.text('Confidential · Prepared by M-II Operations, LLC', pageW - margin, pageH - 40, {align:'right'});

  // === HELPER FOR CONTENT PAGES ===
  let y = 0;
  function newPage(){
    doc.addPage();
    // top accent
    doc.setFillColor(...NAVY);
    doc.rect(0, 0, pageW, 36, 'F');
    doc.setFillColor(...ACCENT);
    doc.rect(0, 36, pageW, 2, 'F');
    doc.setTextColor(255,255,255);
    doc.setFont('helvetica','bold');
    doc.setFontSize(10);
    doc.text('M-II OPERATIONS · OPERATIONAL AUDIT', margin, 23);
    doc.setFont('helvetica','normal');
    doc.setTextColor(...SILVER_2);
    doc.setFontSize(9);
    doc.text(company, pageW - margin, 23, {align:'right'});
    // footer
    doc.setTextColor(...INK_3);
    doc.setFontSize(8);
    doc.text('Confidential · ' + today, margin, pageH - 28);
    const pn = 'Page ' + doc.internal.getNumberOfPages();
    doc.text(pn, pageW - margin, pageH - 28, {align:'right'});
    y = 78;
  }
  function checkPage(needed){
    if(y + needed > pageH - 60) newPage();
  }
  function h2(text){
    checkPage(36);
    doc.setTextColor(...NAVY);
    doc.setFont('helvetica','bold');
    doc.setFontSize(18);
    doc.text(text, margin, y);
    y += 8;
    doc.setDrawColor(...ACCENT);
    doc.setLineWidth(1.5);
    doc.line(margin, y, margin + 40, y);
    y += 22;
  }
  function h3(text){
    checkPage(28);
    doc.setTextColor(...NAVY);
    doc.setFont('helvetica','bold');
    doc.setFontSize(13);
    doc.text(text, margin, y);
    y += 18;
  }
  function para(text, color){
    checkPage(20);
    doc.setTextColor(...(color||INK_2));
    doc.setFont('helvetica','normal');
    doc.setFontSize(10.5);
    const lines = doc.splitTextToSize(text, contentW);
    lines.forEach(line => { checkPage(14); doc.text(line, margin, y); y += 13; });
    y += 4;
  }

  // === EXECUTIVE SUMMARY ===
  newPage();
  h2('Executive Summary');

  // Contact strip — 8 fields in a 4-col x 2-row grid, each cell holds label + multi-line value
  const colW = contentW / 4;
  const stripH = 92;
  doc.setFillColor(...BG);
  doc.rect(margin, y, contentW, stripH, 'F');
  doc.setDrawColor(...SILVER_2);
  doc.setLineWidth(0.4);
  doc.rect(margin, y, contentW, stripH);
  const stripCells = [
    {label:'COMPANY',       value: company},
    {label:'CONTACT',       value: name || '—'},
    {label:'INDUSTRY',      value: state.contact.industry || '—'},
    {label:'REVENUE RANGE', value: state.contact.revenue  || '—'},
    {label:'HEADCOUNT',     value: state.contact.headcount|| '—'},
    {label:'LOCATION',      value: state.contact.location || '—'},
    {label:'ASSESSED',      value: today},
    {label:'ANSWERED',      value: s.totalAnswered + ' / 100'}
  ];
  stripCells.forEach((c, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    const cx = margin + 12 + colW * col;
    const cy = y + 18 + row * (stripH/2);
    doc.setTextColor(...INK_3);
    doc.setFont('helvetica','bold');
    doc.setFontSize(7.5);
    doc.text(c.label, cx, cy);
    doc.setTextColor(...INK);
    doc.setFont('helvetica','bold');
    doc.setFontSize(10);
    const lines = doc.splitTextToSize(String(c.value || '—'), colW - 18);
    // show up to 2 lines, then ellipsize if more
    const display = lines.slice(0, 2);
    if(lines.length > 2) display[1] = display[1].replace(/.{0,3}$/, '…');
    display.forEach((line, li) => { doc.text(line, cx, cy + 14 + li * 12); });
  });
  y += stripH + 14;

  // Overall maturity hero
  const interpColor = overall.label === 'Strong' ? GREEN : overall.label === 'Partial Build' ? GOLD : RED;
  doc.setFillColor(...NAVY);
  doc.rect(margin, y, contentW, 80, 'F');
  doc.setTextColor(...SILVER_2);
  doc.setFont('helvetica','bold');
  doc.setFontSize(9);
  doc.text('OVERALL OPERATIONAL MATURITY', margin+18, y+22);
  doc.setTextColor(255,255,255);
  doc.setFont('helvetica','bold');
  doc.setFontSize(44);
  doc.text(pctText, margin+18, y+62);
  doc.setFont('helvetica','normal');
  doc.setFontSize(11);
  doc.setTextColor(...SILVER_2);
  doc.text(s.totalScore + ' of ' + s.totalMax + ' possible points', margin+18, y+76);
  // right side
  doc.setFillColor(...ACCENT);
  doc.rect(pageW - margin - 140, y, 140, 80, 'F');
  doc.setTextColor(...NAVY);
  doc.setFont('helvetica','bold');
  doc.setFontSize(9);
  doc.text('TIER', pageW - margin - 124, y+22);
  doc.setFontSize(16);
  doc.text(overall.label, pageW - margin - 124, y+46, {maxWidth: 120});
  y += 100;

  para(overall.note);

  // Tier breakdown table
  h3('Tier Breakdown');
  const rowH = 28;
  const colWs = [contentW*0.32, contentW*0.16, contentW*0.16, contentW*0.36];
  // header
  doc.setFillColor(...NAVY);
  doc.rect(margin, y, contentW, rowH, 'F');
  doc.setTextColor(255,255,255);
  doc.setFont('helvetica','bold');
  doc.setFontSize(9);
  let cx = margin + 10;
  ['TIER','SCORE','MATURITY','INTERPRETATION'].forEach((h,i)=>{ doc.text(h, cx, y+18); cx += colWs[i]; });
  y += rowH;
  TIERS.forEach((t,idx) => {
    const td = s.byTier[t.name] || {score:0,max:0};
    const pct = td.max ? td.score/td.max : 0;
    const interp = interpret(pct);
    const ic = interp.label==='Strong'?GREEN: interp.label==='Partial Build'?GOLD : RED;
    if(idx%2===0){ doc.setFillColor(250,251,253); doc.rect(margin, y, contentW, rowH, 'F'); }
    doc.setDrawColor(...SILVER_2);
    doc.setLineWidth(0.4);
    doc.line(margin, y+rowH, margin+contentW, y+rowH);
    cx = margin + 10;
    doc.setTextColor(...INK);
    doc.setFont('helvetica','bold');
    doc.setFontSize(11);
    doc.text(t.name, cx, y+18); cx += colWs[0];
    doc.setFont('helvetica','normal');
    doc.text(td.score+'/'+td.max, cx, y+18); cx += colWs[1];
    doc.setFont('helvetica','bold');
    doc.setTextColor(...ic);
    doc.text((pct*100).toFixed(0)+'%', cx, y+18); cx += colWs[2];
    doc.setFont('helvetica','normal');
    doc.setTextColor(...INK_2);
    doc.setFontSize(9.5);
    doc.text(interp.label, cx, y+18);
    y += rowH;
  });
  y += 14;

  // Risk-weighted summary
  h3('Risk-Weighted View');
  para('High-severity items represent the touchpoints where gaps most directly threaten revenue, compliance, or founder freedom. Below is how the operation performs across each severity band.');
  const sevRows = ['High','Medium','Low'].map(sev => {
    const d = s.bySeverity[sev];
    const pct = d.max ? d.score/d.max : 0;
    return {sev, score:d.score, max:d.max, pct, answered:d.answered, total:d.total};
  });
  sevRows.forEach(r => {
    checkPage(36);
    const barW = contentW - 200;
    const fillW = barW * r.pct;
    const c = r.sev==='High'?RED: r.sev==='Medium'?GOLD : GREEN;
    doc.setTextColor(...INK);
    doc.setFont('helvetica','bold');
    doc.setFontSize(10);
    doc.text(r.sev + ' Risk', margin, y+10);
    doc.setFont('helvetica','normal');
    doc.setTextColor(...INK_3);
    doc.setFontSize(9);
    doc.text(r.score+'/'+r.max+' pts · '+r.answered+'/'+r.total+' answered', margin, y+22);
    // bar bg
    doc.setFillColor(...SILVER_2);
    doc.rect(margin + 130, y+6, barW, 14, 'F');
    doc.setFillColor(...c);
    doc.rect(margin + 130, y+6, fillW, 14, 'F');
    doc.setTextColor(...INK);
    doc.setFont('helvetica','bold');
    doc.setFontSize(10);
    doc.text((r.pct*100).toFixed(0)+'%', margin + 130 + barW + 10, y+17);
    y += 32;
  });
  y += 8;

  // === IMPACT AREAS ===
  newPage();
  h2('Impact Areas');
  para('Scores grouped by the operational function each touchpoint affects. Use this to identify which capability area drives the most leverage in your next 90 days.');
  const cats = Object.keys(s.byCategory).sort((a,b)=>{
    const pa = s.byCategory[a].max ? s.byCategory[a].score/s.byCategory[a].max : 0;
    const pb = s.byCategory[b].max ? s.byCategory[b].score/s.byCategory[b].max : 0;
    return pa - pb;
  });
  cats.forEach(cat => {
    const d = s.byCategory[cat];
    const pct = d.max ? d.score/d.max : 0;
    const interp = interpret(pct);
    const c = interp.label==='Strong'?GREEN: interp.label==='Partial Build'?GOLD : RED;
    checkPage(50);
    doc.setFillColor(...BG);
    doc.rect(margin, y, contentW, 44, 'F');
    doc.setDrawColor(...c);
    doc.setLineWidth(3);
    doc.line(margin, y, margin, y+44);
    doc.setLineWidth(0.4);
    doc.setTextColor(...NAVY);
    doc.setFont('helvetica','bold');
    doc.setFontSize(12);
    doc.text(cat, margin + 14, y+18);
    doc.setFont('helvetica','normal');
    doc.setTextColor(...INK_3);
    doc.setFontSize(9);
    doc.text(d.score+' of '+d.max+' pts · '+d.total+' touchpoints', margin + 14, y+34);
    doc.setFont('helvetica','bold');
    doc.setFontSize(20);
    doc.setTextColor(...c);
    const pctStr = (pct*100).toFixed(0)+'%';
    doc.text(pctStr, pageW - margin - 14, y+22, {align:'right'});
    doc.setFontSize(9);
    doc.setTextColor(...INK_2);
    doc.text(interp.label, pageW - margin - 14, y+36, {align:'right'});
    y += 52;
  });

  // === PRIORITIZED RECOMMENDATIONS ===
  newPage();
  h2('Prioritized Action Plan');
  para('Items below are sorted by impact (risk severity) and effort to close (score). High-severity gaps scored 0 are the first priorities — they represent the touchpoints most likely to threaten revenue continuity, founder freedom, or compliance.');

  function sevRank(s){return s==='High'?0:s==='Medium'?1:2;}
  const priorityGaps = s.gaps.slice().sort((a,b) => sevRank(a.severity) - sevRank(b.severity) || a.n - b.n);
  const priorityPartials = s.partials.slice().sort((a,b) => sevRank(a.severity) - sevRank(b.severity) || a.n - b.n);

  if(priorityGaps.length){
    h3('Tier 1 · Close Critical Gaps (' + priorityGaps.length + ')');
    para('These touchpoints scored "Not in place." Start here — especially High-severity items.');
    priorityGaps.forEach((q,i) => {
      checkPage(46);
      const c = q.severity==='High'?RED: q.severity==='Medium'?GOLD : GREEN;
      doc.setFillColor(255,255,255);
      doc.setDrawColor(...SILVER_2);
      doc.setLineWidth(0.4);
      doc.rect(margin, y, contentW, 40);
      doc.setFillColor(...c);
      doc.rect(margin, y, 4, 40, 'F');
      doc.setTextColor(...INK);
      doc.setFont('helvetica','bold');
      doc.setFontSize(10);
      doc.text('#'+q.n, margin + 12, y+14);
      doc.setFont('helvetica','normal');
      doc.setFontSize(9);
      doc.setTextColor(...INK_3);
      doc.text(q.tier + ' · ' + q.impact + ' · ' + q.severity + ' Risk', margin + 40, y+14);
      doc.setTextColor(...INK);
      doc.setFontSize(10);
      const lines = doc.splitTextToSize(q.q, contentW - 24);
      doc.text(lines[0], margin + 12, y+30);
      if(lines.length > 1) doc.text(lines[1] || '', margin + 12, y+40);
      y += (lines.length > 1 ? 52 : 46);
    });
    y += 4;
  }

  if(priorityPartials.length){
    checkPage(40);
    h3('Tier 2 · Strengthen Partial Builds (' + priorityPartials.length + ')');
    para('These touchpoints scored "Partial." They exist but are inconsistent. Reinforce these after critical gaps are closed.');
    priorityPartials.forEach(q => {
      checkPage(34);
      const c = q.severity==='High'?RED: q.severity==='Medium'?GOLD : GREEN;
      doc.setFillColor(255,255,255);
      doc.setDrawColor(...SILVER_2);
      doc.setLineWidth(0.4);
      doc.rect(margin, y, contentW, 28);
      doc.setFillColor(...c);
      doc.rect(margin, y, 4, 28, 'F');
      doc.setTextColor(...INK);
      doc.setFont('helvetica','bold');
      doc.setFontSize(10);
      doc.text('#'+q.n, margin + 12, y+12);
      doc.setFont('helvetica','normal');
      doc.setTextColor(...INK_3);
      doc.setFontSize(8.5);
      doc.text(q.impact + ' · ' + q.severity, margin + 40, y+12);
      doc.setTextColor(...INK_2);
      doc.setFontSize(9.5);
      const oneline = doc.splitTextToSize(q.q, contentW - 24)[0];
      doc.text(oneline, margin + 12, y+24);
      y += 32;
    });
    y += 4;
  }

  if(s.unanswered.length){
    checkPage(40);
    h3('Unanswered (' + s.unanswered.length + ')');
    para('These touchpoints were not scored. They are not included in your maturity score and represent information gaps to revisit before your review call.');
    const lines = s.unanswered.map(q => '#'+q.n+' · '+q.q).join('  •  ');
    doc.setTextColor(...INK_3);
    doc.setFontSize(9);
    const split = doc.splitTextToSize(lines, contentW);
    split.forEach(l => { checkPage(12); doc.text(l, margin, y); y += 12; });
  }

  // === FULL RESPONSE LOG ===
  newPage();
  h2('Full Response Log');
  para('Every touchpoint and your score, in question order. Use this as the working document during your review call with Randy.');
  const tableRowH = 16;
  // Header
  doc.setFillColor(...NAVY);
  doc.rect(margin, y, contentW, tableRowH+4, 'F');
  doc.setTextColor(255,255,255);
  doc.setFont('helvetica','bold');
  doc.setFontSize(8.5);
  const cWidths = [28, contentW*0.58, contentW*0.18, contentW*0.10, 30];
  let xx = margin + 6;
  ['#','TOUCHPOINT','IMPACT','SEV','SCORE'].forEach((h,i)=>{
    if(i===4) doc.text(h, margin + contentW - 6, y+14, {align:'right'});
    else doc.text(h, xx, y+14);
    xx += cWidths[i];
  });
  y += tableRowH + 4;

  QUESTIONS.forEach((q,i) => {
    if(y + tableRowH > pageH - 60) newPage();
    const a = state.answers[q.n];
    if(i%2===0){ doc.setFillColor(250,251,253); doc.rect(margin, y, contentW, tableRowH, 'F'); }
    doc.setDrawColor(...SILVER_2);
    doc.setLineWidth(0.2);
    doc.line(margin, y+tableRowH, margin+contentW, y+tableRowH);
    xx = margin + 6;
    doc.setTextColor(...INK_3);
    doc.setFont('helvetica','normal');
    doc.setFontSize(8);
    doc.text(String(q.n), xx, y+11); xx += cWidths[0];
    doc.setTextColor(...INK);
    doc.setFontSize(8.5);
    const qtxt = doc.splitTextToSize(q.q, cWidths[1] - 8)[0];
    doc.text(qtxt, xx, y+11); xx += cWidths[1];
    doc.setTextColor(...INK_2);
    doc.setFontSize(8);
    doc.text(q.impact, xx, y+11); xx += cWidths[2];
    const sc = q.severity==='High'?RED: q.severity==='Medium'?GOLD : GREEN;
    doc.setTextColor(...sc);
    doc.setFont('helvetica','bold');
    doc.text(q.severity, xx, y+11); xx += cWidths[3];
    // score
    const scoreText = a === undefined ? '—' : String(a);
    const scoreColor = a === undefined ? INK_3 : a===2 ? GREEN : a===1 ? GOLD : RED;
    doc.setTextColor(...scoreColor);
    doc.setFont('helvetica','bold');
    doc.setFontSize(9);
    doc.text(scoreText, margin + contentW - 6, y+11, {align:'right'});
    y += tableRowH;
  });

  // === NEXT STEPS ===
  newPage();
  h2('Next Steps');
  para('Your audit results have been forwarded to Randy Derrick at M-II Operations. He will reach out within one business day to schedule your complimentary 30-minute review call (phone or Zoom).');
  h3('What to prepare for the call');
  const prep = [
    'Bring this report. Randy will walk through your lowest-scoring tier and impact area first.',
    'Be ready to discuss two or three specific situations from the last 90 days where a gap on this report cost time, money, or sleep.',
    'Identify the one outcome that would matter most to you in the next 90 days — Randy will use this as the anchor for any recommended next steps.',
    'Decide who else from your team should be on the call. If only you can answer the questions, only you should attend.'
  ];
  prep.forEach(p => {
    checkPage(40);
    doc.setFillColor(...ACCENT);
    doc.circle(margin + 6, y+5, 3, 'F');
    doc.setTextColor(...INK_2);
    doc.setFont('helvetica','normal');
    doc.setFontSize(10.5);
    const lines = doc.splitTextToSize(p, contentW - 24);
    lines.forEach((line,i)=>{ doc.text(line, margin + 18, y + 9 + i*14); });
    y += Math.max(20, lines.length * 14 + 10);
  });

  // Final contact card
  y += 10;
  checkPage(120);
  doc.setFillColor(...NAVY);
  doc.rect(margin, y, contentW, 110, 'F');
  doc.setFillColor(...ACCENT);
  doc.rect(margin, y, 4, 110, 'F');
  doc.setTextColor(...SILVER_2);
  doc.setFont('helvetica','bold');
  doc.setFontSize(9);
  doc.text('YOUR M-II CONTACT', margin + 20, y+22);
  doc.setTextColor(255,255,255);
  doc.setFont('helvetica','bold');
  doc.setFontSize(18);
  doc.text('Randy Derrick', margin + 20, y+46);
  doc.setFont('helvetica','normal');
  doc.setFontSize(11);
  doc.setTextColor(...SILVER_2);
  doc.text('Founder & COO · M-II Operations, LLC', margin + 20, y+64);
  doc.text('Randy.Derrick@miiops.com', margin + 20, y+82);
  doc.text('Waxahachie, Texas', margin + 20, y+98);

  // BUILD BLOB
  const blob = doc.output('blob');
  lastPdfBlob = blob;
  const safeCo = (company || 'Company').replace(/[^A-Za-z0-9_-]+/g,'_');
  lastPdfFilename = 'M-II_Operational_Audit_' + safeCo + '.pdf';
  return blob;
}

function downloadBlob(blob, name){
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = name; document.body.appendChild(a); a.click();
  setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 1000);
}

function downloadAgain(){
  if(lastPdfBlob) downloadBlob(lastPdfBlob, lastPdfFilename);
  else alert('PDF not available — please re-submit.');
}

// ============= SUBMIT =============
async function submitAudit(){
  // Validate contact
  if(!state.contact.email || !state.contact.company || !state.contact.name){
    alert('Please go back and complete the required contact fields (Company, Name, Email).');
    goTo('contact'); return;
  }
  const btn = document.getElementById('submit-btn');
  const status = document.getElementById('submit-status');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generating report…';
  status.innerHTML = '<div class="alert alert-info"><div>Generating your PDF report…</div></div>';

  let pdfBlob;
  try {
    pdfBlob = await generatePDF();
  } catch(e){
    console.error(e);
    status.innerHTML = '<div class="alert alert-error"><div><strong>Error generating PDF:</strong> '+escapeHtml(e.message||String(e))+'</div></div>';
    btn.disabled = false; btn.innerHTML = 'Generate Report &amp; Send →';
    return;
  }

  // Download for the user immediately
  downloadBlob(pdfBlob, lastPdfFilename);

  // Build email payload
  const s = computeScores();
  const overallPct = s.totalMax ? s.totalScore/s.totalMax : 0;
  const overall = interpret(overallPct);
  const company = state.contact.company || 'Unknown';

  let summary = `OPERATIONAL AUDIT — ${company}\n`;
  summary += `Submitted: ${new Date().toLocaleString()}\n\n`;
  summary += `--- CONTACT ---\n`;
  summary += `Company: ${state.contact.company || '-'}\n`;
  summary += `Name:    ${state.contact.name || '-'}\n`;
  summary += `Role:    ${state.contact.role || '-'}\n`;
  summary += `Email:   ${state.contact.email || '-'}\n`;
  summary += `Phone:   ${state.contact.phone || '-'}\n`;
  summary += `Industry:${state.contact.industry || '-'}\n`;
  summary += `Revenue: ${state.contact.revenue || '-'}\n`;
  summary += `Headcount: ${state.contact.headcount || '-'}\n`;
  summary += `Location: ${state.contact.location || '-'}\n\n`;
  summary += `--- OVERALL ---\n`;
  summary += `Maturity: ${(overallPct*100).toFixed(0)}% (${s.totalScore}/${s.totalMax}) — ${overall.label}\n`;
  summary += `Answered: ${s.totalAnswered}/100\n\n`;
  summary += `--- BY TIER ---\n`;
  TIERS.forEach(t=>{ const d=s.byTier[t.name]||{score:0,max:0}; const p=d.max?d.score/d.max:0; summary += `${t.name}: ${d.score}/${d.max} (${(p*100).toFixed(0)}%) — ${interpret(p).label}\n`; });
  summary += `\n--- BY IMPACT AREA ---\n`;
  Object.keys(s.byCategory).forEach(c=>{ const d=s.byCategory[c]; const p=d.max?d.score/d.max:0; summary += `${c}: ${d.score}/${d.max} (${(p*100).toFixed(0)}%)\n`; });
  summary += `\n--- HIGH-SEVERITY GAPS (scored 0) ---\n`;
  const highGaps = s.gaps.filter(q=>q.severity==='High');
  if(highGaps.length===0) summary += '(none)\n';
  else highGaps.forEach(q=>{ summary += `#${q.n} [${q.impact}] ${q.q}\n`; });
  summary += `\n--- FULL RESPONSES ---\n`;
  QUESTIONS.forEach(q=>{ const a = state.answers[q.n]; summary += `#${q.n} [${a===undefined?'-':a}] ${q.q}\n`; });

  // Submit to Web3Forms
  status.innerHTML = '<div class="alert alert-info"><div>Sending results to Randy…</div></div>';
  const subject = `Operational Audit — ${company}`;

  let sendOk = false;
  let sendErr = '';

  if(WEB3FORMS_KEY && !WEB3FORMS_KEY.startsWith('REPLACE_')){
    try {
      const fd = new FormData();
      fd.append('access_key', WEB3FORMS_KEY);
      fd.append('subject', subject);
      fd.append('from_name', 'M-II Operational Audit');
      fd.append('to', EMAIL_TO);
      fd.append('reply_to', state.contact.email || '');
      fd.append('email', state.contact.email || '');
      fd.append('company', company);
      fd.append('contact_name', state.contact.name || '');
      fd.append('phone', state.contact.phone || '');
      fd.append('overall_maturity_pct', (overallPct*100).toFixed(0)+'%');
      fd.append('overall_label', overall.label);
      fd.append('message', summary);
      // Attach PDF
      fd.append('attachment', pdfBlob, lastPdfFilename);

      const res = await fetch('https://api.web3forms.com/submit', {method:'POST', body: fd});
      const data = await res.json();
      if(data.success){ sendOk = true; }
      else { sendErr = data.message || 'Submission failed'; }
    } catch(e){
      sendErr = e.message || String(e);
    }
  } else {
    sendErr = 'Web3Forms access key not configured.';
  }

  // Show result + fallback
  const detail = document.getElementById('done-detail');
  if(sendOk){
    detail.innerHTML = `<div><strong>✓ Sent to Randy.</strong> Your results email and PDF attachment were delivered to ${EMAIL_TO}. You'll hear back within one business day.</div>`;
    goTo('done');
  } else {
    // Fallback: mailto with summary
    const mailto = 'mailto:' + EMAIL_TO + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(summary.slice(0, 1800) + '\n\n[Full PDF report was downloaded to the submitter\'s device — please request the attachment from ' + (state.contact.email||'sender') + ' if not included.]');
    detail.innerHTML = `
      <div>
        <strong>⚠ PDF downloaded, but automatic email delivery failed.</strong>
        <br />Reason: ${escapeHtml(sendErr)}
        <br /><br />
        <strong>Two options to get the results to Randy:</strong>
        <ol style="margin:8px 0 0 18px">
          <li><a href="${mailto}">Click here to open a pre-filled email</a> — attach the downloaded PDF and send.</li>
          <li>Email <a href="mailto:${EMAIL_TO}">${EMAIL_TO}</a> directly with the subject "${escapeHtml(subject)}" and the downloaded PDF attached.</li>
        </ol>
      </div>`;
    goTo('done');
  }
}
</script>
</body>
</html>
'''

html = html.replace('__LOGO_B64__', logo_b64)
html = html.replace('__QUESTIONS_JSON__', questions_min)

with open(OUTPUT_PATH, 'w') as f:
    f.write(html)

print("Wrote:", os.path.getsize(OUTPUT_PATH), "bytes ->", OUTPUT_PATH)
