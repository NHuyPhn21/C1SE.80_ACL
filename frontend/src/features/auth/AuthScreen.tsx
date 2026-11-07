import { FormEvent, useState } from "react";
import { login, register, requestPasswordReset } from "../../api";

export type AuthSession = {
  user: { id: string; email: string; full_name: string; role: string };
  accessToken: string;
};

export function AuthScreen({ onAuthenticated }: { onAuthenticated: (session: AuthSession) => void }) {
  const [mode, setMode] = useState<"login" | "register" | "forgot">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (mode === "forgot") {
      setBusy(true);
      try { setSuccess((await requestPasswordReset(email)).message); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to send the reset link."); } finally { setBusy(false); }
      return;
    }
    if (mode === "register" && password !== confirmPassword) { setError("Passwords do not match. Please re-enter your password."); return; }
    if (mode === "register" && !acceptedTerms) { setError("Please agree to the Terms of Service and Privacy Policy."); return; }
    setBusy(true);
    try {
      const result = mode === "login" ? await login(email, password, rememberMe) : await register(fullName, email, password);
      onAuthenticated({ user: result.user, accessToken: result.tokens.access_token });
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to authenticate."); } finally { setBusy(false); }
  };

  return <main className="auth-page"><section className="auth-rail"><div><div className="auth-brand"><span className="auth-brand-icon">✣</span><strong>ACL</strong></div><p className="auth-subtitle">Automated Comic Localization</p><div className="version-pill"><span /> v2.4 Editorial Core <b>•</b> Engine Online</div></div><div className="auth-promise"><span className="auth-kicker">PRODUCTION INGESTION</span><h1>{mode === "login" ? <>One pipeline,<br />from raw scan to<br />typeset page.</> : mode === "register" ? <>Build your team<br />workspace.</> : <>We will get you<br />back in.</>}</h1><ul><li>Detection, OCR, translation and inpainting in one queue</li><li>Team workspace with role-based review</li><li>Keep terminology consistent with a shared glossary</li></ul></div><footer>© 2026 Team C1SE.80 <span>Terms　 ·　 Privacy</span></footer></section><section className="auth-main"><div className="environment-pill"><span /> Cluster: US-East Production <b>?</b></div><form className={`login-card ${mode === "register" ? "register-card" : ""} ${mode === "forgot" ? "forgot-card" : ""}`} onSubmit={(event) => void submit(event)}>{mode !== "forgot" ? <div className="auth-tabs"><button type="button" className={mode === "login" ? "active" : ""} onClick={() => { setMode("login"); setError(""); }}>Log in</button><button type="button" className={mode === "register" ? "active" : ""} onClick={() => { setMode("register"); setError(""); }}>Register</button></div> : <button type="button" className="back-login" onClick={() => { setMode("login"); setError(""); setSuccess(""); }}>← Back to log in</button>}{mode === "forgot" && <div className="reset-icon">⚿</div>}<h2>{mode === "login" ? "Welcome back" : mode === "register" ? "Create your account" : "Reset your password"}</h2><p className="login-intro">{mode === "login" ? "Sign in to continue to your workspace." : mode === "register" ? "You will be able to create or join a Project after signing up." : "Enter the email on your account and we will send you a secure reset link."}</p>{error && <div className="auth-error"><strong>!</strong><span>{error}</span></div>}{success && <div className="reset-success">✓　{success} Check your spam folder if it does not appear.</div>}{mode === "register" && <><label htmlFor="full-name">Full name</label><div className="auth-input"><input id="full-name" value={fullName} onChange={(event) => setFullName(event.target.value)} required /></div></>}<label htmlFor="email">Email</label><div className={`auth-input ${error ? "has-error" : ""}`}><input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>{mode !== "forgot" && <><div className="password-label"><label htmlFor="password">Password</label><small>At least 8 characters</small></div><div className={`auth-input ${error ? "has-error" : ""}`}><input id="password" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required /><button type="button" className="password-toggle" onClick={() => setShowPassword((value) => !value)}>{showPassword ? "◉" : "⊙"}</button></div></>}{mode === "register" && <><label className="password-label plain-label" htmlFor="confirm-password">Confirm password</label><div className="auth-input"><input id="confirm-password" type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required /></div><label className="terms-check"><input type="checkbox" checked={acceptedTerms} onChange={(event) => setAcceptedTerms(event.target.checked)} /> I agree to the Terms of Service and Privacy Policy</label></>}{mode === "login" && <div className="login-options"><label><input type="checkbox" checked={rememberMe} onChange={(event) => setRememberMe(event.target.checked)} /> Remember me</label><button type="button" className="link-button" onClick={() => setMode("forgot")}>Forgot password?</button></div>}<button className="login-button" disabled={busy}>{busy ? "Processing..." : mode === "login" ? "Log in  →" : mode === "register" ? "Create account  →" : "Send reset link  ▷"}</button></form><div className="auth-build">● ACL-Engine v2.4 (Build 8821)　|　Target: Japanese / English Dual-Stack</div></section></main>;
}
