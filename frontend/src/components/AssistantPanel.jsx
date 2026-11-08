import { useEffect, useRef, useState } from "react";
import { api } from "../api";

const SpeechRecognitionImpl = typeof window !== "undefined"
  ? window.SpeechRecognition || window.webkitSpeechRecognition
  : null;
const canSpeak = typeof window !== "undefined" && "speechSynthesis" in window;

/** Assistant chat. Type a question, or press the microphone and ask out loud. */
export default function AssistantPanel() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [speakAnswers, setSpeakAnswers] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! Ask me about risk, budget, team workload, health or what to do next. You can also press the microphone and ask out loud." },
  ]);
  const recognition = useRef(null);

  useEffect(() => {
    return () => {
      recognition.current?.abort();
      if (canSpeak) window.speechSynthesis.cancel();
    };
  }, []);

  function speak(text) {
    if (!speakAnswers || !canSpeak) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  }

  async function ask(question) {
    const q = question.trim();
    if (!q || busy) return;
    setError("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setBusy(true);
    try {
      const res = await api("/assistant/ask", { method: "POST", body: { question: q } });
      setMessages((m) => [...m, { role: "bot", text: res.answer }]);
      speak(res.answer);
    } catch (err) {
      setMessages((m) => [...m, { role: "bot", text: "Error: " + err.message }]);
    } finally {
      setBusy(false);
    }
  }

  function send(e) {
    e.preventDefault();
    ask(input);
  }

  function startListening() {
    setError("");
    if (!SpeechRecognitionImpl) {
      setError("Voice input needs Google Chrome or Microsoft Edge.");
      return;
    }
    const rec = new SpeechRecognitionImpl();
    rec.lang = "en-IN";
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (event) => {
      const heard = event.results[0][0].transcript;
      setInput(heard);
      ask(heard);
    };
    rec.onerror = (event) => {
      const reasons = {
        "not-allowed": "Microphone access was blocked. Allow it in the address bar and try again.",
        "no-speech": "I didn't hear anything. Try again and speak clearly.",
        network: "Voice needs an internet connection in this browser.",
      };
      setError(reasons[event.error] || `Voice error: ${event.error}`);
    };
    rec.onend = () => setListening(false);
    recognition.current = rec;
    setListening(true);
    rec.start();
  }

  function stopListening() {
    recognition.current?.stop();
    setListening(false);
  }

  return (
    <>
      <button className="assistant-fab" onClick={() => setOpen(!open)} aria-label="Open assistant">
        {open ? "×" : "AI"}
      </button>
      {open && (
        <div className="assistant-panel">
          <div className="assistant-head">
            <span>StratifyIQ Assistant</span>
            <label className="voice-toggle">
              <input type="checkbox" checked={speakAnswers} onChange={(e) => {
                setSpeakAnswers(e.target.checked);
                if (!e.target.checked && canSpeak) window.speechSynthesis.cancel();
              }} />
              Speak answers
            </label>
          </div>
          <div className="assistant-body">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>{m.text}</div>
            ))}
            {busy && <div className="msg bot">Thinking...</div>}
            {error && <div className="msg bot error-msg">{error}</div>}
          </div>
          <form className="assistant-input" onSubmit={send}>
            <button
              type="button"
              className={`mic ${listening ? "listening" : ""}`}
              onClick={listening ? stopListening : startListening}
              aria-label={listening ? "Stop listening" : "Ask by voice"}
              title={listening ? "Stop listening" : "Ask by voice"}
            >
              {listening ? "Stop" : "Mic"}
            </button>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={listening ? "Listening..." : "Ask about your projects..."}
            />
            <button type="submit" disabled={busy}>Send</button>
          </form>
        </div>
      )}
    </>
  );
}
