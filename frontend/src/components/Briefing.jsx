import { useEffect, useState } from "react";
import { api } from "../api";

export default function Briefing() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => () => window.speechSynthesis?.cancel(), []);

  async function generate() {
    setLoading(true);
    setError("");
    try {
      setData(await api("/briefing"));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function readAloud() {
    if (!("speechSynthesis" in window)) {
      setError("Voice is not supported in this browser. Try Chrome or Edge.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(data.text);
    utterance.rate = 1;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  }

  function stop() {
    window.speechSynthesis?.cancel();
    setSpeaking(false);
  }

  return (
    <div className="card briefing">
      <div className="row">
        <h3>Morning briefing</h3>
        <button onClick={generate} disabled={loading}>
          {loading ? "Writing..." : "Generate briefing"}
        </button>
        {data && (
          <button onClick={speaking ? stop : readAloud}>{speaking ? "Stop" : "Read aloud"}</button>
        )}
      </div>
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <p className="briefing-text">{data.text}</p>
          <span className="chip">{data.source === "ai" ? "Written by AI" : "Written from the rules"}</span>
        </>
      )}
    </div>
  );
}
