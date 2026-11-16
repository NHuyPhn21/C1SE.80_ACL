
import { FormEvent, useEffect, useState } from "react";
import { resetPassword, verifyResetToken } from "../../api";

export function ResetPasswordScreen({ onBackToLogin }: { onBackToLogin?: () => void }) {
  const token = new URLSearchParams(window.location.search).get("token") ?? "";

  const [tokenStatus, setTokenStatus] = useState<"checking" | "valid" | "invalid">("checking");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const goBackToLogin = () => {
    if (onBackToLogin) {
      onBackToLogin();
    } else {
      window.location.assign("/");
    }
  };

  useEffect(() => {
    let active = true;

    if (!token) {
      setTokenStatus("invalid");
      return;
    }

    verifyResetToken(token)
      .then((result) => {
        if (active) setTokenStatus(result.valid ? "valid" : "invalid");
      })
      .catch(() => {
        if (active) {
          setTokenStatus("invalid");
          setError("Unable to verify the reset link. Please try again.");
        }
      });

    return () => {
      active = false;
    };
  }, [token]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setBusy(true);
    try {
      await resetPassword(token, password);
      setSuccess(true);
      window.history.replaceState({}, "", "/reset-password");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reset password.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-rail">
        <div>
          <div className="auth-brand">
            <span className="auth-brand-icon">✣</span>
            <strong>ACL</strong>
          </div>
          <p className="auth-subtitle">Automated Comic Localization</p>
          <div className="version-pill">
            <span /> v2.4 Editorial Core <b>•</b> Engine Online
          </div>
        </div>
        <div className="auth-promise">
          <span className="auth-kicker">ACCOUNT RECOVERY</span>
          <h1>
            Securely reset
            <br />
            your workspace
            <br />
            credentials.
          </h1>
          <ul>
            <li>Single-use cryptographic recovery token</li>
            <li>Instant access restoration across all projects</li>
            <li>Protected with salted password hashing</li>
          </ul>
        </div>
        <footer>
          © 2026 Team C1SE.80 <span>Terms　 ·　 Privacy</span>
        </footer>
      </section>

      <section className="auth-main">
        <div className="environment-pill">
          <span /> Cluster: US-East Production <b>?</b>
        </div>
        <form className="login-card forgot-card" onSubmit={handleSubmit}>
          <button type="button" className="back-login" onClick={goBackToLogin}>
            ← Back to log in
          </button>
          <div className="reset-icon">⚿</div>
          <h2>Set a new password</h2>
          <p className="login-intro">
            Choose a strong password (at least 8 characters) for your ACL account.
          </p>

          {success ? (
            <>
              <div className="reset-success">
                ✓　Your password has been reset successfully. You can now sign in with your new
                password.
              </div>
              <button type="button" className="login-button" onClick={goBackToLogin}>
                Back to log in →
              </button>
            </>
          ) : tokenStatus === "checking" ? (
            <p className="muted">Verifying your reset link...</p>
          ) : tokenStatus === "invalid" ? (
            <>
              <div className="auth-error">
                <strong>!</strong>
                <span>{error || "This reset link is invalid or has expired."}</span>
              </div>
              <button type="button" className="login-button" onClick={goBackToLogin}>
                Back to log in →
              </button>
            </>
          ) : (
            <>
              {error && (
                <div className="auth-error">
                  <strong>!</strong>
                  <span>{error}</span>
                </div>
              )}

              <div className="password-label">
                <label htmlFor="new-password">New password</label>
                <small>At least 8 characters</small>
              </div>
              <div className={`auth-input ${error ? "has-error" : ""}`}>
                <input
                  id="new-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={8}
                  autoComplete="new-password"
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((value) => !value)}
                >
                  {showPassword ? "◉" : "⊙"}
                </button>
              </div>

              <label className="password-label plain-label" htmlFor="confirm-new-password">
                Confirm new password
              </label>
              <div className={`auth-input ${error ? "has-error" : ""}`}>
                <input
                  id="confirm-new-password"
                  type={showPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  minLength={8}
                  autoComplete="new-password"
                  required
                />
              </div>

              <button className="login-button" disabled={busy}>
                {busy ? "Processing..." : "Reset password →"}
              </button>
            </>
          )}
        </form>
        <div className="auth-build">
          ● ACL-Engine v2.4 (Build 8821)　|　Target: Japanese / English Dual-Stack
        </div>
      </section>
    </main>
  );
}
