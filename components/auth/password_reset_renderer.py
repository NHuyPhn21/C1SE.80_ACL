"""Streamlit component for the Figma password-reset flow."""

from functools import lru_cache
from typing import Any

import streamlit as st

from components.auth.assets import load_auth_assets


@lru_cache(maxsize=1)
def _get_password_reset_component() -> Any:
    assets = load_auth_assets()
    html = f"""
<main class="shell">
  <aside class="brand">
    <div class="brand-top">
      <div class="brand-lockup"><div class="mark">ACL</div><div><div class="brand-name">ACL</div><div class="brand-sub">Automated Comic Localization</div></div></div>
      <div class="engine"><i></i>v2.4 Editorial Core &bull; Engine Online</div>
    </div>
    <section class="brand-copy">
      <h1>We will get you<br>back in.</h1>
      <p>Password reset emails are delivered securely through SendGrid and expire after a short window for security.</p>
      <div class="security-list">
        <div><span class="security-icon">&#128274;</span>Encrypted TLS 1.3 Transmission</div>
        <div><span class="security-icon">&#128273;</span>Automated Single-Use Token Delivery</div>
        <div><span class="security-icon">&#9993;</span>SendGrid High-Deliverability Relays</div>
      </div>
    </section>
    <footer><span>&copy; 2026 Team C1SE.80</span><span>Terms &nbsp;&bull;&nbsp; Privacy</span></footer>
  </aside>
  <section class="canvas">
    <div class="relay">&#9671; SendGrid Prod Relay: cluster-ap-east</div>
    <article class="card">
      <button class="back" data-login>&larr; Back to log in</button>
      <div class="key-icon">&#128273;</div>

      <section id="requestView">
        <h2>Reset your password</h2>
        <p class="lead">Enter the email on your account and we will send you a secure reset link.</p>
        <div id="requestAlert" class="alert error"></div>
        <form id="requestForm">
          <label for="resetEmail">Email</label>
          <div class="input-wrap"><input id="resetEmail" type="email" placeholder="you@studio.com" autocomplete="email" required><span>@</span></div>
          <button class="primary" type="submit">Send reset link <img src="{assets['arrow']}" alt=""></button>
        </form>
        <div id="sentPanel" class="sent hidden">
          <span class="sent-check">&#10003;</span>
          <div>If an account exists for that email, a reset link will arrive within a few minutes. Check your spam folder if it does not appear.</div>
        </div>
      </section>

      <section id="resetView" class="hidden">
        <h2>Create a new password</h2>
        <p class="lead">Your link is verified. Choose a new password for your account.</p>
        <div id="resetAlert" class="alert error"></div>
        <form id="resetForm">
          <label for="newPassword">New password</label>
          <div class="input-wrap"><input id="newPassword" type="password" placeholder="At least 8 characters" autocomplete="new-password" minlength="8" required><button type="button" class="eye" data-target="newPassword"><img src="{assets['eye']}" alt="Show password"></button></div>
          <label for="confirmPassword">Confirm new password</label>
          <div class="input-wrap"><input id="confirmPassword" type="password" placeholder="Repeat your new password" autocomplete="new-password" minlength="8" required><button type="button" class="eye" data-target="confirmPassword"><img src="{assets['eye']}" alt="Show password"></button></div>
          <button class="primary" type="submit">Update password <img src="{assets['arrow']}" alt=""></button>
        </form>
      </section>

      <section id="invalidView" class="hidden state-view">
        <h2>Reset link unavailable</h2>
        <p class="lead">This link is invalid, expired, or has already been used. Request a new secure link to continue.</p>
        <button id="requestAgain" class="primary">Request another link</button>
      </section>

      <section id="successView" class="hidden state-view">
        <div class="success-icon">&#10003;</div>
        <h2>Password updated</h2>
        <p class="lead">Your password has been changed successfully. You can now log in with your new password.</p>
        <button class="primary" data-login>Continue to log in <img src="{assets['arrow']}" alt=""></button>
      </section>

      <div class="support">Need administrator intervention? <b>Contact Studio Support</b></div>
    </article>
    <div class="technical">&bull; ACL-Engine v2.4 (Build 8821) | Transactional Delivery: SendGrid API v3 | SOC2 Certified Ingestion</div>
  </section>
</main>
"""
    css = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600&family=Sora:wght@600;700&display=swap');
:host{display:block;color:#1c1a17;background:#f4f7f2;font-family:'Plus Jakarta Sans',sans-serif;--navy:#25326f;--ground:#f4f7f2;--line:#e4dfd6;--copy:#55545d;--green:#2f7a4f;--danger:#c1382e}
*{box-sizing:border-box}html,body{margin:0;background:var(--ground)}button,input{font:inherit}.shell{min-height:1024px;display:grid;grid-template-columns:384px minmax(0,1fr)}
.brand{position:relative;overflow:hidden;min-height:1024px;padding:40px;color:#fff;background:var(--navy);display:flex;flex-direction:column}.brand:before{content:"";position:absolute;width:370px;height:370px;right:-120px;top:-150px;border:1px solid rgba(255,255,255,.08);border-radius:50%;box-shadow:0 0 0 28px rgba(255,255,255,.035),0 0 0 58px rgba(255,255,255,.025)}
.brand-top,.brand-copy,.brand footer{position:relative;z-index:1}.brand-lockup{display:flex;align-items:center;gap:12px}.mark{width:40px;height:40px;border-radius:7px;border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.08);display:grid;place-items:center;font:600 18px 'Sora',sans-serif}.brand-name{font:700 26px/30px 'Sora',sans-serif}.brand-sub{color:rgba(255,255,255,.78);font-size:13px}.engine{display:inline-flex;align-items:center;margin-top:24px;padding:4px 12px;border:1px solid rgba(255,255,255,.2);border-radius:999px;background:rgba(255,255,255,.08);font-size:11px}.engine i{width:7px;height:7px;margin-right:7px;border-radius:50%;background:#34d399}
.brand-copy{margin:auto 0}.brand h1{margin:0 0 18px;font:700 36px/1.25 'Sora',sans-serif;letter-spacing:-.8px}.brand-copy>p{max-width:302px;margin:0;color:rgba(255,255,255,.88);font-size:15px;line-height:25px}.security-list{display:grid;gap:14px;margin-top:40px}.security-list>div{min-height:54px;padding:12px 15px;border:1px solid rgba(255,255,255,.15);border-radius:11px;background:rgba(255,255,255,.06);display:flex;align-items:center;gap:13px;font-size:13px;font-weight:500}.security-icon{width:28px;height:28px;border-radius:7px;background:rgba(255,255,255,.1);display:grid;place-items:center;font-size:14px}.brand footer{padding-top:18px;border-top:1px solid rgba(255,255,255,.14);display:flex;justify-content:space-between;color:rgba(255,255,255,.62);font-size:12px}
.canvas{position:relative;min-width:0;min-height:1024px;padding:48px;display:flex;align-items:center;justify-content:center}.relay{position:absolute;right:48px;top:49px;padding:6px 12px;border:1px solid var(--line);border-radius:999px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.06);color:#4b4b53;font:400 11px 'JetBrains Mono',monospace}.card{width:460px;min-height:626px;padding:40px;background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 1px 2px rgba(0,0,0,.05)}.back{margin:0 0 26px;padding:0;border:0;background:transparent;color:#3d3d46;font-weight:600;cursor:pointer}.key-icon{width:48px;height:48px;margin-bottom:18px;border:1px solid var(--line);border-radius:12px;background:#eef0f8;color:var(--navy);display:grid;place-items:center;font-size:20px}.card h2{margin:0 0 8px;font:700 30px/1.25 'Sora',sans-serif;letter-spacing:-.7px}.lead{margin:0 0 26px;color:var(--copy);font-size:15px;line-height:24px}.card form{display:grid;gap:10px}.card label{font-size:13px;font-weight:600}.input-wrap{position:relative;margin-bottom:10px}.input-wrap input{width:100%;height:44px;padding:0 44px 0 15px;border:1px solid var(--line);border-radius:8px;outline:none;color:#1c1a17;background:#fff;font-size:14px}.input-wrap input:focus{border-color:var(--navy);box-shadow:0 0 0 1px var(--navy)}.input-wrap>span{position:absolute;right:14px;top:11px;color:#777883;font-size:19px}.eye{position:absolute;right:6px;top:7px;width:30px;height:30px;padding:7px;border:0;background:transparent;cursor:pointer}.eye img{width:16px;height:16px}.primary{width:100%;height:46px;margin-top:0;border:0;border-radius:999px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;gap:8px;font-family:'Sora',sans-serif;font-size:13px;font-weight:600;cursor:pointer}.primary img{width:12px;height:12px}.sent{margin-top:22px;padding:15px;border:1px solid #a8c8b5;border-radius:8px;background:#e7f1ea;color:var(--green);display:flex;align-items:flex-start;gap:11px;font-size:12px;line-height:18px}.sent-check{width:18px;height:18px;flex:none;border:1px solid var(--green);border-radius:50%;display:grid;place-items:center;font-size:11px;font-weight:700}.alert{margin:0 0 16px;padding:12px 14px;border-radius:8px;font-size:12px;line-height:18px}.alert:empty{display:none}.error{border:1px solid #e0a39d;background:#f9e7e4;color:var(--danger)}.support{margin-top:22px;padding-top:22px;border-top:1px solid var(--line);text-align:center;color:#666670;font-size:12px}.support b{color:var(--navy)}.state-view{padding-top:12px}.success-icon{width:48px;height:48px;margin-bottom:18px;border-radius:50%;background:#e7f1ea;color:var(--green);display:grid;place-items:center;font-size:22px;font-weight:700}.technical{position:absolute;bottom:58px;color:#777883;font:400 10px 'JetBrains Mono',monospace}.hidden{display:none!important}
@media(max-width:850px){.shell{display:block;min-height:100vh}.brand{min-height:auto;padding:24px}.brand-copy{margin:52px 0 24px}.brand h1{font-size:30px}.security-list,.brand footer{display:none}.canvas{min-height:auto;padding:36px 18px 60px}.relay,.technical{display:none}.card{width:100%;max-width:460px;min-height:0;padding:26px 22px}.card h2{font-size:26px}}
"""
    js = f"""export default function(component) {{
const {{parentElement,setTriggerValue,data}}=component;
const requestView=parentElement.querySelector('#requestView'),resetView=parentElement.querySelector('#resetView'),invalidView=parentElement.querySelector('#invalidView'),successView=parentElement.querySelector('#successView');
function show(view){{[requestView,resetView,invalidView,successView].forEach(node=>node.classList.add('hidden'));view.classList.remove('hidden');}}
parentElement.querySelectorAll('[data-login]').forEach(button=>button.addEventListener('click',()=>setTriggerValue('action',{{kind:'navigate_login',requestId:Date.now()}})));
parentElement.querySelector('#requestAgain').addEventListener('click',()=>show(requestView));
parentElement.querySelector('#requestForm').addEventListener('submit',event=>{{event.preventDefault();setTriggerValue('action',{{kind:'request_reset',email:parentElement.querySelector('#resetEmail').value.trim(),requestId:Date.now()}});}});
parentElement.querySelector('#resetForm').addEventListener('submit',event=>{{event.preventDefault();setTriggerValue('action',{{kind:'reset_password',password:parentElement.querySelector('#newPassword').value,confirmPassword:parentElement.querySelector('#confirmPassword').value,requestId:Date.now()}});}});
parentElement.querySelectorAll('.eye').forEach(button=>button.addEventListener('click',()=>{{const input=parentElement.querySelector('#'+button.dataset.target);input.type=input.type==='password'?'text':'password';button.querySelector('img').src=input.type==='password'?'{assets['eye']}':'{assets['eye_off']}';}}));
if(data.completed){{show(successView);}}
else if(data.hasToken){{show(data.tokenValid?resetView:invalidView);}}
else{{show(requestView);}}
if(data.error){{const alert=data.hasToken?parentElement.querySelector('#resetAlert'):parentElement.querySelector('#requestAlert');alert.textContent=data.error;}}
if(data.sent){{parentElement.querySelector('#sentPanel').classList.remove('hidden');parentElement.querySelector('#requestForm').classList.add('hidden');}}
}}"""
    return st.components.v2.component(
        "acl_password_reset", html=html, css=css, js=js, isolate_styles=True
    )


def render_password_reset_ui(
    *,
    has_token: bool,
    token_valid: bool,
    sent: bool = False,
    completed: bool = False,
    error: str | None = None,
) -> dict[str, Any] | None:
    component = _get_password_reset_component()
    result = component(
        key="password-reset",
        data={
            "hasToken": has_token,
            "tokenValid": token_valid,
            "sent": sent,
            "completed": completed,
            "error": error,
        },
        height=1024,
        on_action_change=lambda: None,
    )
    action = result.get("action")
    return action if isinstance(action, dict) else None
