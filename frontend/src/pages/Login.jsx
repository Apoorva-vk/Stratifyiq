import { useState } from "react";
import { api, setToken } from "../api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("admin@demo.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
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

  return (
    <div className="login">
      <form className="card login-card" onSubmit={submit}>
        <h2>StratifyIQ Login</h2>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Log in</button>
      </form>
    </div>
  );
}
