/** Horizontal bars. Each row: { label, value, max, detail, cls } where cls is OK, UNDER or OVER. */
export default function BarList({ rows, emptyText = "Nothing to show yet." }) {
  if (rows.length === 0) return <p className="muted">{emptyText}</p>;
  return (
    <div className="barlist">
      {rows.map((r, i) => {
        const pct = r.max ? Math.min(100, (r.value / r.max) * 100) : 0;
        return (
          <div key={i} className="barrow">
            <div className="barlabel">
              <span>{r.label}</span>
              <small>{r.detail}</small>
            </div>
            <div className="bar wide">
              <span className={r.cls || "OK"} style={{ width: `${pct}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
