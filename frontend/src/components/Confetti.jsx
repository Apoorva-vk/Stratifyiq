import { useEffect, useState } from "react";

const COLORS = ["#1f3a5f", "#17a46b", "#e0a100", "#d64545", "#5b8def"];

/** Short confetti burst. Change the trigger value to fire it again. */
export default function Confetti({ trigger }) {
  const [pieces, setPieces] = useState([]);

  useEffect(() => {
    if (!trigger) return undefined;
    const batch = Array.from({ length: 28 }, (_, i) => ({
      id: `${trigger}-${i}`,
      left: Math.random() * 100,
      delay: Math.random() * 0.3,
      drift: (Math.random() - 0.5) * 160,
      color: COLORS[i % COLORS.length],
    }));
    setPieces(batch);
    const timer = setTimeout(() => setPieces([]), 1800);
    return () => clearTimeout(timer);
  }, [trigger]);

  return (
    <div className="confetti-layer" aria-hidden="true">
      {pieces.map((p) => (
        <span
          key={p.id}
          className="confetti-piece"
          style={{ left: `${p.left}%`, background: p.color, animationDelay: `${p.delay}s`, "--drift": `${p.drift}px` }}
        />
      ))}
    </div>
  );
}
