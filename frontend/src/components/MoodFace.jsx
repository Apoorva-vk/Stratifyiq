/** A small face showing a project's health at a glance. */
export default function MoodFace({ health }) {
  const mood = health >= 75 ? "happy" : health >= 50 ? "neutral" : "worried";
  const color = mood === "happy" ? "#17a46b" : mood === "neutral" ? "#e0a100" : "#d64545";
  const mouth = mood === "happy" ? "M10 20 Q16 27 22 20" : mood === "neutral" ? "M10 23 L22 23" : "M10 27 Q16 20 22 27";
  return (
    <svg width="34" height="34" viewBox="0 0 32 32" className={`mood mood-${mood}`} role="img" aria-label={`${mood} project`}>
      <circle cx="16" cy="16" r="14" fill={color} fillOpacity="0.2" stroke={color} strokeWidth="2" />
      <circle className="eye" cx="11" cy="13" r="2" fill="#1d2433" />
      <circle className="eye" cx="21" cy="13" r="2" fill="#1d2433" />
      <path d={mouth} stroke="#1d2433" strokeWidth="2" fill="none" strokeLinecap="round" />
    </svg>
  );
}
