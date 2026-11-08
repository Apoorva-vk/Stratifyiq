import { useState } from "react";
import { api, setToken } from "../api";
import BrandPanel from "../components/BrandPanel";
import PasswordInput from "../components/PasswordInput";

/** Sign up, log in, forgot password, reset password and accept invitation, in one screen. */
export default function Auth({ onLogin, startMode = "login", inviteToken = "", resetToken = "", verifyToken = "" }) {
  const [mode, setMode] = useState(startMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [reset, setReset] = useState(resetToken);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [resendEmail, setResendEmail] = useState("");
  const [confirmed, setConfirmed] = useState(false);

  function go(next) {
    setMode(next);
    setError("");
    setInfo("");
  }

  async function login(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/auth/login", { method: "POST", body: { email, password } });
      setToken(data.access_token);
      onLogin();
    } catch (err) {
      setError(err.message);
    }
  }

  async function signup(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/auth/signup", {
        method: "POST",
        body: { company_name: companyName, full_name: name, email, password },
      });
      setInfo(data.message + (data.verify_link ? ` Development link: ${data.verify_link}` : ""));
      setMode("login");
    } catch (err) {
      setError(err.message);
    }
  }

  async function confirmEmail() {
    setError("");
    try {
      await api("/auth/verify", { method: "POST", body: { token: verifyToken } });
      setConfirmed(true);
    } catch (err) {
      setError(err.message);
    }
  }

  async function resend(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await api("/auth/resend-verification", { method: "POST", body: { email: resendEmail || email } });
      setInfo(res.message + (res.verify_link ? ` Development link: ${res.verify_link}` : ""));
    } catch (err) {
      setError(err.message);
    }
  }

  async function forgot(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await api("/auth/forgot-password", { method: "POST", body: { email } });
      setInfo(res.message);
      if (res.reset_token) {
        setReset(res.reset_token);
        setInfo("Email is not set up, so the reset token is shown here (development mode).");
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function resetPassword(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/auth/reset-password", { method: "POST", body: { token: reset, password } });
      setPassword("");
      setReset("");
      setMode("login");
      setInfo("Password updated. You can now log in.");
    } catch (err) {
      setError(err.message);
    }
  }

  async function accept(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/auth/accept-invite", {
        method: "POST",
        body: { token: inviteToken, full_name: name, password },
      });
      setToken(data.access_token);
      onLogin();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="login">
      <BrandPanel />
      <div className="card login-card">
        {mode === "login" && (
          <form onSubmit={login} className="login-card">
            <h2>StratifyIQ Login</h2>
            <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
            <label>Password<PasswordInput required value={password} onChange={(e) => setPassword(e.target.value)} /></label>
            {info && <p className="success">{info}</p>}
            {error && <p className="error">{error}</p>}
            <button type="submit">Log in</button>
            {error.includes("confirm your email") && (
              <button type="button" className="link-btn" onClick={(e) => resend(e)}>Resend confirmation email</button>
            )}
            <button type="button" className="link-btn" onClick={() => go("signup")}>Create a new account</button>
            <button type="button" className="link-btn" onClick={() => go("forgot")}>Forgot password?</button>
          </form>
        )}

        {mode === "signup" && (
          <form onSubmit={signup} className="login-card">
            <h2>Create your account</h2>
            <p className="muted small">You'll be the Admin of your new company workspace.</p>
            <label>Company name<input required minLength={2} value={companyName} onChange={(e) => setCompanyName(e.target.value)} /></label>
            <label>Your full name<input required minLength={2} value={name} onChange={(e) => setName(e.target.value)} /></label>
            <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
            <label>Password (at least 8 characters)<PasswordInput required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} /></label>
            {error && <p className="error">{error}</p>}
            <button type="submit">Sign up</button>
            <button type="button" className="link-btn" onClick={() => go("login")}>Already have an account? Log in</button>
          </form>
        )}

        {mode === "forgot" && (
          <form onSubmit={forgot} className="login-card">
            <h2>Reset password</h2>
            <label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
            {info && <p className="success">{info}</p>}
            {error && <p className="error">{error}</p>}
            <button type="submit">Send reset link</button>
            <button type="button" onClick={() => go("reset")}>I have a reset link</button>
            <button type="button" className="link-btn" onClick={() => go("login")}>Back to login</button>
          </form>
        )}

        {mode === "reset" && (
          <form onSubmit={resetPassword} className="login-card">
            <h2>Choose a new password</h2>
            <label>Reset token<input value={reset} onChange={(e) => setReset(e.target.value)} /></label>
            <label>New password (at least 8 characters)<PasswordInput value={password} onChange={(e) => setPassword(e.target.value)} /></label>
            {error && <p className="error">{error}</p>}
            <button type="submit">Update password</button>
            <button type="button" className="link-btn" onClick={() => go("login")}>Back to login</button>
          </form>
        )}

        {mode === "verify" && (
          <div className="login-card">
            <h2>Confirm your email</h2>
            {!confirmed ? (
              <>
                <p className="muted">Click the button to confirm this email address for your StratifyIQ account.</p>
                {error && <p className="error">{error}</p>}
                <button onClick={confirmEmail}>Confirm my email</button>
              </>
            ) : (
              <>
                <p className="success">Email confirmed. You can now log in.</p>
                <button onClick={() => { window.history.replaceState({}, "", "/"); setMode("login"); }}>Go to login</button>
              </>
            )}
          </div>
        )}

        {mode === "invite" && (
          <form onSubmit={accept} className="login-card">
            <h2>Accept your invitation</h2>
            <label>Full name<input value={name} onChange={(e) => setName(e.target.value)} /></label>
            <label>Choose a password (at least 8 characters)<PasswordInput value={password} onChange={(e) => setPassword(e.target.value)} /></label>
            {error && <p className="error">{error}</p>}
            <button type="submit">Join StratifyIQ</button>
          </form>
        )}
      </div>
    </div>
  );
}
