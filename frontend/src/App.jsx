import { useEffect, useState } from "react";
import { api, getToken, clearToken } from "./api";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import Team from "./pages/Team";
import Simulator from "./pages/Simulator";
import Reports from "./pages/Reports";
import Activity from "./pages/Activity";
import Insights from "./pages/Insights";
import Organisation from "./pages/Organisation";
import AssistantPanel from "./components/AssistantPanel";
import Notifications from "./components/Notifications";
import Logo from "./components/Logo";
import { initReveal } from "./motion";
import Landing from "./components/Landing";

const PAGES = [
  ["dashboard", "Dashboard"],
  ["projects", "Projects"],
  ["team", "Team"],
  ["organisation", "Organisation"],
  ["simulator", "Simulator"],
  ["reports", "Reports"],
  ["insights", "Insights"],
  ["activity", "Activity"],
];

// Links from emails open the app with ?invite=... or ?reset=...
const params = new URLSearchParams(window.location.search);
const inviteToken = params.get("invite") || "";
const resetToken = params.get("reset") || "";
const verifyToken = params.get("verify") || "";
const startMode = inviteToken ? "invite" : resetToken ? "reset" : verifyToken ? "verify" : "login";
if (inviteToken || resetToken || verifyToken) clearToken();

export default function App() {
  const [authed, setAuthed] = useState(!!getToken());
  const [view, setView] = useState("dashboard");
  const [projectId, setProjectId] = useState(null);
  const [showLogin, setShowLogin] = useState(!!inviteToken || !!resetToken || !!verifyToken);

  useEffect(() => initReveal(), [view, authed, showLogin]);

  const [role, setRole] = useState(null);
  useEffect(() => {
    if (authed) api("/auth/me").then((u) => setRole(u.role)).catch(() => setRole(null));
  }, [authed]);
  const [dark, setDark] = useState(localStorage.getItem("theme") !== "light");

  useEffect(() => {
    document.body.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  if (!authed && !showLogin) {
    return <Landing onEnter={() => setShowLogin(true)} />;
  }
  if (!authed) {
    return (
      <Auth
        startMode={startMode}
        inviteToken={inviteToken}
        resetToken={resetToken}
        verifyToken={verifyToken}
        onLogin={() => {
          window.history.replaceState({}, "", "/");
          setAuthed(true);
        }}
      />
    );
  }

  function logout() {
    clearToken();
    setAuthed(false);
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="brand"><Logo size={30} /><span>StratifyIQ</span></span>
        <nav>
          {PAGES.map(([key, label]) => (
            <button key={key} className={view === key ? "active" : ""} onClick={() => setView(key)}>
              {label}
            </button>
          ))}
        </nav>
        <div className="top-actions">
          <Notifications />
          <button className="bell" onClick={() => setDark(!dark)}>{dark ? "Light" : "Dark"}</button>
          <button onClick={logout}>Logout</button>
        </div>
      </header>
      <main>
        {view === "dashboard" && (
          <Dashboard
            onSimulate={(id) => {
              setProjectId(id);
              setView("simulator");
            }}
          />
        )}
        {view === "projects" && <Projects />}
        {view === "team" && <Team />}
        {view === "organisation" && <Organisation />}
        {view === "simulator" && <Simulator projectId={projectId} setProjectId={setProjectId} />}
        {view === "reports" && <Reports />}
        {view === "insights" && <Insights />}
        {view === "activity" && <Activity />}
      </main>
      <footer className="site-footer">
        <div>
          <div className="foot-brand"><Logo size={28} /> StratifyIQ</div>
          <p>Decision intelligence for projects, budgets and teams.</p>
        </div>
        <div className="foot-links">
          {PAGES.map(([key, label]) => (
            <button key={key} className="link-btn" onClick={() => setView(key)}>{label}</button>
          ))}
        </div>
        <p className="foot-copy">© {new Date().getFullYear()} StratifyIQ. All rights reserved.</p>
      </footer>
      <AssistantPanel />
    </div>
  );
}
