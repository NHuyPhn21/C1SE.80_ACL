"""Bidirectional Streamlit component for the ACL authentication screens."""

from functools import lru_cache
from typing import Any

import streamlit as st

from components.auth.assets import load_auth_assets


def _build_auth_document(initial_view: str) -> str:
    if initial_view not in {"login", "register"}:
        raise ValueError(f"Unsupported authentication view: {initial_view}")

    assets = load_auth_assets()

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600&family=Sora:wght@600;700&display=swap');
:host {{
  display:block;
  color:#1c1a17;
  background:#f7faf5;
  font-family:'Plus Jakarta Sans',sans-serif;
  --navy:#25326f; --ground:#f7faf5; --paper:#fff; --ink:#1c1a17;
  --muted:#767681; --copy:#454650; --lavender:#71689f; --line:#e4dfd6; --danger:#c1382e;
  --danger-bg:#f8e2de; --green:#2f7a4f;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; min-height:100%; background:var(--ground); color:var(--ink); font-family:'Plus Jakarta Sans',sans-serif; }}
button,input {{ font:inherit; }} button {{ cursor:pointer; }}
.shell {{ min-height:1024px; display:grid; grid-template-columns:384px minmax(0,1fr); background:var(--ground); }}
.shell.login-mode:not(.login-error) {{ --ground:#f4f7f2; }}
.brand {{ min-height:1024px; position:relative; overflow:hidden; padding:40px 40px 34px; color:#fff; background:var(--navy); border-right:1px solid rgba(228,223,214,.2); display:flex; flex-direction:column; }}
.brand:before {{ content:""; position:absolute; inset:0; opacity:.035; background-image:linear-gradient(90deg,#fff 3.125%,transparent 3.125%),linear-gradient(180deg,#fff 3.125%,transparent 3.125%); background-size:32px 32px; pointer-events:none; }}
.brand-top,.brand-copy,.brand-foot {{ position:relative; z-index:1; }}
.brand-lockup {{ display:flex; align-items:center; gap:12px; }}
.brand-identity {{ min-width:0; }}
.mark {{ width:36px; height:36px; border:1px solid rgba(255,255,255,.2); border-radius:8px; background:rgba(255,255,255,.1); display:grid; place-items:center; box-shadow:inset 0 2px 4px rgba(0,0,0,.05); }}
.mark img {{ width:18px; height:18px; }}
.mark.register-mark {{ width:40px; height:40px; border-radius:12px; background:#fff; color:var(--navy); font:700 15px/1 'Sora',sans-serif; }}
.brand-name {{ font:700 26px/32px 'Sora',sans-serif; letter-spacing:-.65px; }}
.brand-sub {{ margin-top:1px; color:rgba(255,255,255,.8); font-size:13px; line-height:18px; letter-spacing:.65px; white-space:nowrap; }}
.badges {{ display:flex; gap:8px; margin-top:16px; flex-wrap:wrap; }}
.badge {{ border:1px solid rgba(255,255,255,.2); background:rgba(255,255,255,.15); border-radius:999px; padding:3px 10px; font:400 12px/18px 'JetBrains Mono',monospace; color:rgba(255,255,255,.9); }}
.badge.online {{ color:#a7f3d0; background:rgba(16,185,129,.2); border-color:rgba(52,211,153,.3); font-family:'Plus Jakarta Sans',sans-serif; font-weight:600; }}
.badge.error-status {{ display:none; align-items:center; gap:8px; padding:4px 10px; background:rgba(255,255,255,.1); border-color:rgba(255,255,255,.15); }}
.dot {{ display:inline-block; width:6px; height:6px; border-radius:50%; margin-right:6px; background:#34d399; vertical-align:1px; }}
.brand-copy {{ margin:auto 0; padding:40px 0; }}
.eyebrow {{ margin:0 0 11px; color:rgba(255,255,255,.7); font-size:11px; font-weight:600; letter-spacing:1.1px; }}
.brand h1 {{ margin:0; font:700 36px/1.25 'Sora',sans-serif; letter-spacing:-.9px; }}
.features {{ display:grid; gap:20px; margin-top:32px; }}
.feature {{ display:grid; grid-template-columns:24px 1fr; gap:14px; align-items:start; color:rgba(255,255,255,.9); font-size:15px; line-height:22px; }}
.feature-icon {{ width:24px; height:24px; margin-top:2px; border:1px solid rgba(255,255,255,.3); background:rgba(255,255,255,.15); border-radius:50%; display:grid; place-items:center; }}
.feature-icon img {{ width:auto; height:auto; }}
.spec {{ display:flex; justify-content:space-between; gap:12px; margin-top:30px; padding-top:17px; border-top:1px solid rgba(255,255,255,.15); color:rgba(255,255,255,.66); font:400 11px/18px 'JetBrains Mono',monospace; white-space:nowrap; }}
.spec-copy {{ display:flex; align-items:center; gap:6px; }} .spec-copy img {{ width:11.25px; height:11.25px; }}
.register-copy .features {{ gap:24px; }}
.register-copy .feature {{ grid-template-columns:28px 1fr; gap:16px; line-height:24px; }}
.register-copy .feature-icon {{ width:24px; height:24px; }}
.register-copy .spec {{ justify-content:flex-start; color:rgba(255,255,255,.8); }}
.brand-foot {{ border-top:1px solid rgba(255,255,255,.14); padding-top:17px; display:flex; justify-content:space-between; color:rgba(255,255,255,.6); font-size:13px; line-height:19px; }}
.legal {{ display:flex; gap:13px; }}
.canvas {{ min-width:0; min-height:1024px; position:relative; display:flex; align-items:center; justify-content:center; padding:48px; }}
.cluster {{ position:absolute; right:32px; top:24px; display:flex; align-items:center; gap:10px; }}
.cluster-pill {{ border:1px solid var(--line); border-radius:999px; background:#fff; padding:7px 13px; box-shadow:0 1px 1px rgba(0,0,0,.05); color:var(--copy); font-size:11px; font-weight:600; letter-spacing:.22px; }}
.cluster .help {{ width:32px; height:32px; border:1px solid var(--line); border-radius:50%; background:#fff; color:var(--copy); display:grid; place-items:center; }} .cluster .help img {{ width:14.17px; height:14.17px; }}
.auth-wrap {{ width:100%; max-width:480px; display:flex; flex-direction:column; align-items:center; gap:16px; }}
.card {{ width:100%; max-width:460px; padding:41px; background:var(--paper); border:1px solid var(--line); border-radius:16px; box-shadow:0 4px 6px -1px rgba(0,0,0,.1),0 2px 4px -2px rgba(0,0,0,.1); }}
.register-card {{ max-width:480px; padding:37px; box-shadow:0 1px 1px rgba(0,0,0,.05); }}
.tabs {{ height:34px; display:grid; grid-template-columns:1fr 1fr; border-bottom:1px solid var(--line); margin-bottom:22px; }}
.tab {{ border:0; background:transparent; color:var(--copy); font-size:13px; font-weight:600; position:relative; padding:0 4px 14px; }}
.tab.active {{ color:var(--navy); }}
.tab.active:after {{ content:""; position:absolute; left:0; right:0; bottom:-1px; height:2px; background:var(--navy); }}
.login-card .tabs {{ display:flex; gap:32px; height:31px; margin-bottom:25px; }} .login-card .tab {{ width:auto; color:var(--lavender); font:500 16px/24px 'Sora',sans-serif; padding-bottom:17px; }} .login-card .tab.active {{ color:var(--navy); font-weight:600; }}
.heading {{ margin-bottom:19px; }}
.heading h2 {{ margin:0 0 5px; font:700 26px/1.3 'Sora',sans-serif; letter-spacing:-.65px; }}
.heading p {{ margin:0; color:var(--copy); font-size:13px; line-height:20px; }}
.login-card .heading {{ margin-bottom:22px; }} .login-card .heading h2 {{ font-size:28px; line-height:42px; }} .login-card .heading p {{ color:var(--lavender); line-height:18px; }}
.alert {{ display:none; align-items:flex-start; gap:10px; margin:-2px 0 17px; padding:13px 14px; color:var(--danger); background:var(--danger-bg); border:1px solid var(--danger); border-radius:8px; font-size:12px; font-weight:600; line-height:17px; }}
.alert img {{ width:15px; height:17px; flex:none; }}
.form {{ display:grid; gap:14px; }} .login-card .form {{ gap:16px; }} .field {{ display:grid; gap:6px; }}
.field-head {{ display:flex; justify-content:space-between; gap:12px; }}
label {{ font-size:13px; line-height:18px; font-weight:500; }}
.hint {{ color:var(--muted); font:400 11px/18px 'JetBrains Mono',monospace; }}
.input-wrap {{ position:relative; }}
.input-wrap input {{ width:100%; height:44px; padding:0 42px 0 15px; color:var(--ink); background:#fff; border:1px solid var(--line); border-radius:8px; outline:none; font-size:13px; }}
.login-mode:not(.login-error) .login-card .input-wrap input {{ font-size:15px; }}
.input-wrap input::placeholder {{ color:var(--muted); opacity:1; }}
.input-wrap input:placeholder-shown + .valid-icon {{ display:none; }}
.input-wrap input:focus {{ border-color:var(--navy); box-shadow:0 0 0 1px var(--navy); }}
.input-icon {{ position:absolute; width:15px; height:15px; right:13px; top:50%; transform:translateY(-50%); object-fit:contain; }}
button.input-icon {{ width:30px; height:30px; right:5px; padding:7px; border:0; background:transparent; }}
.error-text {{ display:none; align-items:center; gap:4px; color:var(--danger); font-size:11px; line-height:15px; font-weight:600; }}
.error-text img {{ width:11px; height:11px; }}
.field.invalid input {{ border:2px solid var(--danger); }} .field.invalid .error-text {{ display:flex; }}
.field.invalid .valid-icon {{ display:block !important; }}
.utility,.terms {{ display:flex; justify-content:space-between; align-items:center; gap:12px; font-size:13px; }}
.terms {{ justify-content:flex-start; }}
.check-label {{ display:flex; align-items:center; gap:8px; cursor:pointer; }}
.check-label input {{ position:absolute; opacity:0; pointer-events:none; }}
.check-box {{ width:16px; height:16px; border:1px solid var(--line); border-radius:4px; background:#fff; display:grid; place-items:center; flex:none; }}
.check-label input:checked + .check-box {{ background:var(--navy); border-color:var(--navy); }}
.check-label input:checked + .check-box:after {{ content:'✓'; color:white; font-size:11px; line-height:1; }}
.login-error #loginForm .check-box {{ background:#fff; border-color:var(--line); }}
.login-error #loginForm .check-box:after {{ content:none; }}
.link {{ color:var(--navy); font-weight:600; text-decoration:none; }}
.tab-link {{ border:0; padding:0; background:transparent; }}
.primary {{ width:100%; height:46px; border:0; border-radius:999px; color:#fff; background:var(--navy); display:flex; align-items:center; justify-content:center; gap:8px; font-family:'Sora',sans-serif; font-size:13px; font-weight:600; box-shadow:0 1px 1px rgba(0,0,0,.05); }}
.login-card .primary {{ font-size:16px; }} .primary img {{ width:12px; height:12px; }}
.card-foot {{ margin-top:24px; padding-top:21px; border-top:1px solid rgba(228,223,214,.7); text-align:center; color:var(--lavender); font-size:13px; }}
.meta {{ color:var(--copy); font:400 10px/16px 'JetBrains Mono',monospace; display:flex; align-items:center; gap:8px; }} .meta img {{ width:10px; height:13px; }}
.canvas-foot {{ position:absolute; bottom:15px; right:32px; color:var(--muted); font:400 11px/16px 'JetBrains Mono',monospace; }}
.login-error .brand {{ justify-content:space-between; }}
.login-error .brand-lockup {{ display:grid; grid-template-columns:36px 1fr; gap:8px 12px; }} .login-error .brand-identity {{ display:contents; }} .login-error .brand-name {{ font-size:24px; line-height:32px; }} .login-error .brand-sub {{ grid-column:1/-1; margin:0; letter-spacing:0; }}
.login-error .badges .badge:not(.error-status) {{ display:none; }} .login-error .badge.error-status {{ display:flex; }}
.login-error .badge.error-status .dot {{ background:#d6eaaf; }}
.login-error .brand-copy {{ margin:0; padding:0; }} .login-error .brand-copy > div:first-of-type {{ margin-top:0; }}
.login-error .features {{ gap:16px; margin-top:24px; }} .login-error .feature {{ grid-template-columns:15px 1fr; gap:12px; line-height:20.63px; }} .login-error .feature-icon {{ width:15px; height:17px; margin:0; border:0; background:transparent; }}
.login-error .spec {{ margin-top:auto; color:rgba(255,255,255,.7); }} .login-error .spec span:last-child {{ color:#d6eaaf; font-weight:500; }}
.login-error .brand-foot {{ border:0; padding-top:12px; }}
.login-error .canvas {{ flex-direction:column; padding:24px; }} .login-error .cluster {{ position:static; width:460px; justify-content:flex-end; margin-bottom:16px; }} .login-error .cluster .help {{ display:none; }}
.login-error .cluster-pill {{ background:#ecefea; padding:5px 13px; font:400 12px/18px 'JetBrains Mono',monospace; }} .login-error .cluster-pill .dot {{ background:var(--danger); }}
.login-error .login-card {{ padding:33px; box-shadow:0 1px 1px rgba(0,0,0,.05); }} .login-error .login-card .tabs {{ gap:0; margin-bottom:20px; }} .login-error .login-card .tab {{ color:var(--muted); font:600 13px/18px 'Plus Jakarta Sans',sans-serif; padding:0 24px 14px; }} .login-error .login-card .tab:first-child {{ padding-left:4px; }} .login-error .login-card .tab.active {{ color:var(--navy); }}
.login-error .login-card .heading {{ margin-bottom:20px; }} .login-error .login-card .heading h2 {{ font-size:24px; line-height:32px; font-weight:600; }} .login-error .login-card .heading p {{ color:var(--copy); }}
.login-error .alert {{ margin:0 0 20px; padding:15px; font-size:13px; line-height:17.88px; }} .login-error .form {{ gap:16px; }} .login-error .field {{ gap:4px; }} .login-error .primary {{ height:44px; font-size:18px; line-height:26px; }}
.login-error .card-foot {{ margin-top:16px; padding-top:17px; color:var(--copy); }} .login-error .canvas-foot {{ position:static; margin-top:24px; }} .login-error .canvas-foot .dot {{ background:var(--muted); }}
.login-error .hint {{ display:none; }}
.register-mode .brand {{ padding:48px; }} .register-mode .brand-copy {{ margin:0; position:absolute; top:315.89px; left:48px; right:48px; padding:0; }} .register-mode .brand-foot {{ position:absolute; left:48px; right:48px; bottom:39px; padding-top:25px; font-size:11px; line-height:14px; font-weight:600; }}
.register-mode .register-copy h1 {{ line-height:42.48px; }} .register-mode .register-copy .features {{ margin-top:32px; gap:24px; }} .register-mode .register-copy .feature {{ grid-template-columns:28px 1fr; gap:16px; line-height:24.38px; font-weight:500; }} .register-mode .register-copy .feature-icon {{ width:28px; height:28px; background:rgba(255,255,255,.1); border-color:rgba(255,255,255,.2); }} .register-mode .register-copy .spec {{ margin-top:32px; padding-top:33px; gap:12px; color:rgba(255,255,255,.8); font-size:12px; font-weight:500; }}
.register-mode .canvas {{ padding:56px; }} .register-mode .register-card .tabs {{ margin-bottom:24px; }} .register-mode .register-card .heading {{ margin-bottom:24px; }} .register-mode .register-card .heading h2 {{ font-size:26px; line-height:32.5px; }} .register-mode .register-card .heading p {{ font-size:13.5px; line-height:21.94px; }} .register-mode .register-card .card-foot {{ margin-top:20px; padding-top:8px; color:var(--copy); }}
.register-error {{ min-height:1070px; }} .register-error .brand {{ min-height:1070px; }} .register-error .canvas {{ min-height:1070px; padding:56px; }} .register-error .register-copy {{ top:338.86px; }} .register-error .register-card {{ padding:37px; }} .register-error .alert {{ margin:-8px 0 14px; padding:13px; font-size:12px; line-height:16.5px; }} .register-error .register-card .heading {{ margin-bottom:16px; }}
.login-error .alert,.register-error .alert {{ display:flex; }} .hidden {{ display:none !important; }}
@media (max-width:850px) {{
  .shell {{ display:block; min-height:100vh; }} .brand {{ min-height:auto; padding:24px; }}
  .brand-copy,.register-mode .brand-copy,.register-error .register-copy {{ position:static; margin:42px 0 20px; padding:0; }} .brand h1 {{ font-size:30px; }}
  .features {{ gap:12px; }} .spec,.brand-foot {{ display:none; }}
  .canvas,.register-mode .canvas,.register-error .canvas {{ min-height:auto; padding:38px 18px 56px; }} .cluster,.canvas-foot {{ display:none; }}
  .card,.register-card {{ padding:25px 22px; }}
  .login-error .brand {{ justify-content:flex-start; }} .login-error .brand-copy {{ margin-top:42px; }} .login-error .login-card,.register-error .register-card {{ padding:25px 22px; }}
}}
</style>
</head>
<body>
<main id="shell" class="shell login-mode">
  <aside class="brand">
    <div class="brand-top">
      <div class="brand-lockup"><div id="brandMark" class="mark"><img src="{assets['logo']}" alt=""></div><div class="brand-identity"><div class="brand-name">ACL</div><div class="brand-sub">Automated Comic Localization</div></div></div>
      <div id="loginBadges" class="badges"><span class="badge">v2.4 Editorial Core</span><span class="badge online"><i class="dot"></i>Engine Online</span><span class="badge error-status"><i class="dot"></i>v2.4 Editorial Core &bull; Engine Online</span></div>
    </div>
    <section id="loginCopy" class="brand-copy">
      <p class="eyebrow">PRODUCTION INGESTION</p><h1>One pipeline,<br>from raw scan to<br>typeset page.</h1>
      <div class="features">
        <div class="feature"><span class="feature-icon"><img src="{assets['check']}" alt=""></span><span>Detection, OCR, translation and<br>inpainting in one queue</span></div>
        <div class="feature"><span class="feature-icon"><img src="{assets['check']}" alt=""></span><span>Dual OCR for Japanese and English<br>source pages</span></div>
        <div class="feature"><span class="feature-icon"><img src="{assets['check']}" alt=""></span><span>Team workspace with role-based<br>review</span></div>
      </div><div class="spec"><span class="spec-copy"><img src="{assets['masking']}" alt="">Precision Masking v2.4</span><span>LATENCY &lt; 280ms</span></div>
    </section>
    <section id="registerCopy" class="brand-copy register-copy hidden">
      <h1>Build your team<br>workspace.</h1>
      <div class="features">
        <div class="feature"><span class="feature-icon"><img src="{assets['register_check']}" alt=""></span><span>Create a Project per series you<br>localize</span></div>
        <div class="feature"><span class="feature-icon"><img src="{assets['register_check']}" alt=""></span><span>Invite Translators and Typesetters<br>by role</span></div>
        <div class="feature"><span class="feature-icon"><img src="{assets['register_check']}" alt=""></span><span>Keep terminology consistent with<br>a shared glossary</span></div>
      </div><div class="spec"><span><i class="dot"></i>v2.4 Editorial Core &bull; Engine Online</span></div>
    </section>
    <footer class="brand-foot"><span>&copy; 2026 Team C1SE.80</span><span class="legal"><span>Terms</span><span>&bull;</span><span>Privacy</span></span></footer>
  </aside>
  <section class="canvas">
    <div id="cluster" class="cluster"><span class="cluster-pill"><i class="dot"></i><span id="clusterText">Cluster: US-East Production</span></span><button class="help"><img src="{assets['help']}" alt="Help"></button></div>
    <div class="auth-wrap">
      <article id="loginCard" class="card login-card">
        <nav class="tabs"><button class="tab active" data-view="login">Log in</button><button class="tab" data-view="register">Register</button></nav>
        <header class="heading"><h2>Welcome back</h2><p>Sign in to continue to your workspace.</p></header>
        <div class="alert"><img src="{assets['alert']}" alt=""><span>Invalid email or password. Please check your<br>credentials and try again.</span></div>
        <form id="loginForm" class="form">
          <div id="loginEmailField" class="field"><label for="loginEmail">Email</label><div class="input-wrap"><input id="loginEmail" type="email" placeholder="you@studio.com" autocomplete="email" required><img class="input-icon valid-icon" src="{assets['valid']}" alt=""></div><div class="error-text"><img src="{assets['error_chevron']}" alt="">Please check this email address.</div></div>
          <div id="loginPasswordField" class="field"><div class="field-head"><label for="loginPassword">Password</label><span class="hint">Min. 8 characters</span></div><div class="input-wrap"><input id="loginPassword" type="password" placeholder="Enter your password" autocomplete="current-password" minlength="8" required><button type="button" class="input-icon password-toggle" data-target="loginPassword" data-eye="{assets['eye']}" data-eye-off="{assets['eye_off']}"><img src="{assets['eye']}" alt="Show password"></button></div><div class="error-text"><img src="{assets['error_chevron']}" alt="">Incorrect password entered.</div></div>
          <div class="utility"><label class="check-label"><input id="rememberMe" type="checkbox"><span class="check-box"></span><span>Remember me</span></label><a class="link" href="#">Forgot password?</a></div>
          <button class="primary" type="submit">Log in <img src="{assets['arrow']}" alt=""></button>
        </form>
        <footer class="card-foot">Don't have an account? <button class="tab-link link" data-view="register">Register</button></footer>
      </article>
      <article id="registerCard" class="card register-card hidden">
        <nav class="tabs"><button class="tab" data-view="login">Log in</button><button class="tab active" data-view="register">Register</button></nav>
        <header class="heading"><h2>Create your account</h2><p>You will be able to create or join a Project after signing up.</p></header>
        <div class="alert"><img src="{assets['register_alert']}" alt=""><span>Please fix the errors below before submitting your<br>registration.</span></div>
        <form id="registerForm" class="form">
          <div class="field"><label for="fullName">Full name</label><div class="input-wrap"><input id="fullName" type="text" placeholder="Your full name" autocomplete="name" required></div></div>
          <div id="registerEmailField" class="field"><label for="registerEmail">Email</label><div class="input-wrap"><input id="registerEmail" type="email" placeholder="you@studio.com" autocomplete="email" required></div><div class="error-text"><img src="{assets['error']}" alt="">This email address is already registered. Please sign in instead.</div></div>
          <div class="field"><label for="registerPassword">Password</label><div class="input-wrap"><input id="registerPassword" type="password" placeholder="At least 8 characters" autocomplete="new-password" minlength="8" required><button type="button" class="input-icon password-toggle" data-target="registerPassword" data-eye="{assets['register_eye']}" data-eye-off="{assets['eye_off']}"><img src="{assets['register_eye']}" alt="Show password"></button></div></div>
          <div id="confirmField" class="field"><label for="confirmPassword">Confirm password</label><div class="input-wrap"><input id="confirmPassword" type="password" placeholder="Repeat password" autocomplete="new-password" minlength="8" required><button type="button" class="input-icon password-toggle" data-target="confirmPassword" data-eye="{assets['register_eye']}" data-eye-off="{assets['eye_off']}"><img src="{assets['register_eye']}" alt="Show password"></button></div><div class="error-text"><img src="{assets['error']}" alt="">Passwords do not match. Please re-enter your password.</div></div>
          <label class="check-label terms"><input id="terms" type="checkbox"><span class="check-box"></span><span>I agree to the <b class="link">Terms of Service</b> and <b class="link">Privacy Policy</b></span></label>
          <button class="primary" type="submit">Create account <img src="{assets['arrow']}" alt=""></button>
        </form>
        <footer class="card-foot">Already have an account? <button class="tab-link link" data-view="login">Log in</button></footer>
      </article>
      <div id="registerMeta" class="meta hidden"><img src="{assets['lock']}" alt="">Encrypted TLS 1.3 &bull; SOC2 Type II Certified Ingestion</div>
    </div>
    <div id="canvasFoot" class="canvas-foot"><i class="dot"></i>ACL-Engine v2.4 (Build 8821) &nbsp;|&nbsp; Target: Japanese / English Dual-Stack</div>
  </section>
</main>
<script>
const shell=parentElement.querySelector('#shell'),loginCard=parentElement.querySelector('#loginCard'),registerCard=parentElement.querySelector('#registerCard'),loginCopy=parentElement.querySelector('#loginCopy'),registerCopy=parentElement.querySelector('#registerCopy'),loginBadges=parentElement.querySelector('#loginBadges'),registerMeta=parentElement.querySelector('#registerMeta'),canvasFoot=parentElement.querySelector('#canvasFoot'),cluster=parentElement.querySelector('#cluster'),brandMark=parentElement.querySelector('#brandMark');
function showView(view){{const register=view==='register';loginCard.classList.toggle('hidden',register);registerCard.classList.toggle('hidden',!register);loginCopy.classList.toggle('hidden',register);registerCopy.classList.toggle('hidden',!register);loginBadges.classList.toggle('hidden',register);registerMeta.classList.toggle('hidden',!register);canvasFoot.classList.toggle('hidden',register);cluster.classList.toggle('hidden',register);brandMark.classList.toggle('register-mark',register);brandMark.innerHTML=register?'ACL':'<img src="{assets['logo']}" alt="">';shell.className='shell '+(register?'register-mode':'login-mode');}}
parentElement.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',event=>{{event.preventDefault();showView(button.dataset.view);setTriggerValue('action',{{kind:'navigate',view:button.dataset.view,requestId:Date.now()}});}}));
parentElement.querySelectorAll('.password-toggle').forEach(button=>button.addEventListener('click',()=>{{const input=parentElement.querySelector('#'+button.dataset.target);input.type=input.type==='password'?'text':'password';button.querySelector('img').src=input.type==='password'?button.dataset.eye:button.dataset.eyeOff;}}));
parentElement.querySelector('#loginForm').addEventListener('submit',event=>{{event.preventDefault();const email=parentElement.querySelector('#loginEmail').value.trim();const password=parentElement.querySelector('#loginPassword').value;const rememberMe=parentElement.querySelector('#rememberMe').checked;setTriggerValue('action',{{kind:'login',email,password,rememberMe,requestId:Date.now()}});}});
parentElement.querySelector('#registerForm').addEventListener('submit',event=>{{event.preventDefault();const fullName=parentElement.querySelector('#fullName').value.trim();const email=parentElement.querySelector('#registerEmail').value.trim();const password=parentElement.querySelector('#registerPassword').value;const confirmPassword=parentElement.querySelector('#confirmPassword').value;const acceptedTerms=parentElement.querySelector('#terms').checked;setTriggerValue('action',{{kind:'register',fullName,email,password,confirmPassword,acceptedTerms,requestId:Date.now()}});}});
showView('{initial_view}');
</script>
</body>
</html>"""

    return html


def _document_parts(document: str) -> tuple[str, str, str]:
    css = document.split("<style>", 1)[1].split("</style>", 1)[0]
    body = document.split("<body>", 1)[1].split("</body>", 1)[0]
    html, script = body.split("<script>", 1)
    script = script.split("</script>", 1)[0]
    return html.strip(), css.strip(), script.strip()


@lru_cache(maxsize=2)
def _get_auth_component(initial_view: str) -> Any:
    html, css, script = _document_parts(_build_auth_document(initial_view))
    javascript = f"""export default function(component) {{
const {{ parentElement, setTriggerValue, data }} = component;
{script}
if (data && data.error) {{
  const view = data.initialView || '{initial_view}';
  shell.classList.add(view + '-error');
  const card = view === 'register' ? registerCard : loginCard;
  const alert = card.querySelector('.alert');
  alert.style.display = 'flex';
  if (view === 'login') {{
    alert.querySelector('span').textContent = 'Invalid email or password. Please check your credentials and try again.';
    brandMark.innerHTML = '<img src="{load_auth_assets()['error_logo']}" alt="">';
    loginCopy.querySelectorAll('.feature-icon img').forEach(icon => icon.src = '{load_auth_assets()['error_check']}');
    loginCard.querySelector('#loginPasswordField .password-toggle img').src = '{load_auth_assets()['eye_off']}';
    parentElement.querySelector('#loginEmailField').classList.add('invalid');
    parentElement.querySelector('#loginPasswordField').classList.add('invalid');
    parentElement.querySelector('#loginEmailField .valid-icon').src = '{load_auth_assets()['input_error']}';
    parentElement.querySelector('#clusterText').textContent = 'AUTH_GATEWAY: HTTP 401 UNAUTHORIZED';
  }} else {{
    alert.querySelector('span').textContent = 'Please fix the errors below before submitting your registration.';
    if (data.error.toLowerCase().includes('passwords do not match')) {{
      parentElement.querySelector('#confirmField').classList.add('invalid');
    }} else if (!data.error.toLowerCase().includes('accept the terms')) {{
      parentElement.querySelector('#registerEmailField').classList.add('invalid');
    }}
  }}
}}
}}"""
    return st.components.v2.component(
        f"acl_auth_{initial_view}",
        html=html,
        css=css,
        js=javascript,
        isolate_styles=True,
    )


def render_auth_ui(
    initial_view: str = "login", error: str | None = None
) -> dict[str, Any] | None:
    """Render the auth form and return a transient user action, if present."""
    if initial_view not in {"login", "register"}:
        raise ValueError(f"Unsupported authentication view: {initial_view}")

    component = _get_auth_component(initial_view)
    result = component(
        key=f"auth-{initial_view}",
        data={"initialView": initial_view, "error": error},
        height=1070 if error and initial_view == "register" else 1024,
        on_action_change=lambda: None,
    )
    action = result.get("action")
    return action if isinstance(action, dict) else None
