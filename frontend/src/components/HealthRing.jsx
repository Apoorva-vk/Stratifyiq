import { useRef } from "react";

/** Animated health ring with a 3D tilt that follows the mouse. */
export default function HealthRing({ value, label }) {
  const ref = useRef(null);
  const v = Math.max(0, Math.min(100, value ?? 0));
  const color = v >= 75 ? "#17a46b" : v >= 50 ? "#e0a100" : "#d64545";

  function onMove(e) {
    const r = ref.current.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    ref.current.style.transform = `rotateY(${x * 20}deg) rotateX(${-y * 20}deg) translateZ(10px)`;
  }
  function onLeave() {
    ref.current.style.transform = "";
  }

  return (
    <div className="tilt-wrap">
      <div className="ring-card tilt" ref={ref} onMouseMove={onMove} onMouseLeave={onLeave}>
        <div
          className="ring"
          style={{ background: `conic-gradient(${color} ${v * 3.6}deg, #e6eaf2 0deg)` }}
        >
          <div className="ring-inner">
            <strong>{value == null ? "—" : Math.round(v)}</strong>
          </div>
        </div>
        <span>{label}</span>
      </div>
    </div>
  );
}
