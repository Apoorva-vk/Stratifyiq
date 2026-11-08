/** StratifyIQ logo mark: an orange hexagon with a stylised "S" bar. */
export default function Logo({ size = 34 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true" className="logo-mark">
      <polygon points="20,2 36,11 36,29 20,38 4,29 4,11" fill="#FF6A13" />
      <path d="M26 12.5 H14 V19.5 H26 V27.5 H14" fill="none" stroke="#FFFFFF" strokeWidth="3.4" strokeLinejoin="miter" />
    </svg>
  );
}
