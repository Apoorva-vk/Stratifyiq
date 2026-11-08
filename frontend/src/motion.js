/**
 * 3D tilt on hover. Cards turn toward the mouse and return flat when it leaves.
 * Nothing slides or animates in from the side or from below.
 */
const SELECTOR = ".card, .score, .lp-pcard, .lp-feature, .ring-card, .lp2-card, .lp2-tile, .lp2-points li";

export function initReveal() {
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) return () => {};

  const move = (e) => {
    const el = e.target.closest && e.target.closest(SELECTOR);
    if (!el) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    el.style.transform = `perspective(900px) rotateX(${(-y * 8).toFixed(2)}deg) rotateY(${(x * 10).toFixed(2)}deg)`;
  };
  const leave = (e) => {
    const el = e.target.closest && e.target.closest(SELECTOR);
    if (el && !el.contains(e.relatedTarget)) el.style.transform = "";
  };
  document.addEventListener("mousemove", move);
  document.addEventListener("mouseout", leave);
  return () => {
    document.removeEventListener("mousemove", move);
    document.removeEventListener("mouseout", leave);
  };
}
