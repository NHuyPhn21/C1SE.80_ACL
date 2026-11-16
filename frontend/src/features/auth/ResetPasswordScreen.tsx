
import { FormEvent, useEffect, useState } from "react";
import { resetPassword, verifyResetToken } from "../../api";

export function ResetPasswordScreen() {
  const token = new URLSearchParams(window.location.search).get("token") ?? "";

  const [tokenStatus, setTokenStatus] = useState<"checking" | "valid" | "invalid">("checking");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

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
      <section className="auth-main">
        <form className="login-card" onSubmit={handleSubmit}>
          <h2>Reset your password</h2>
          <p className="login-intro">Enter and confirm your new password.</p>

          {success ? (
            <>
              <div className="reset-success">
                Your password has been reset successfully.
              </div>
              <button
                type="button"
                className="login-button"
                onClick={() => window.location.assign("/")}
              >
                Back to log in
              </button>
            </>
          ) : tokenStatus === "checking" ? (
            <p>Verifying your reset link...</p>
          ) : tokenStatus === "invalid" ? (
            <>
              <div className="auth-error">
                {error || "This reset link is invalid or has expired."}
              </div>
              <button
                type="button"
                className="login-button"
                onClick={() => window.location.assign("/")}
              >
                Request a new reset link
              </button>
            </>
          ) : (
            <>
              {error && <div className="auth-error">{error}</div>}

              <label htmlFor="new-password">New password</label>
              <div className="auth-input">
                <input
                  id="new-password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={8}
                  autoComplete="new-password"
                  required
                />
              </div>

              <label htmlFor="confirm-new-password">
                Confirm new password
              </label>
              <div className="auth-input">
                <input
                  id="confirm-new-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  autoComplete="new-password"
                  required
                />
              </div>

              <button className="login-button" disabled={busy}>
                {busy ? "Processing..." : "Reset password"}
              </button>
            </>
          )}
        </form>
      </section>
    </main>
  );
}
