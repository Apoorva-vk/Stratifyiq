import Logo from "./Logo";

/** Left side of the login screen: logo, headline, key points and simple artwork below the text. */
export default function BrandPanel() {
  return (
    <aside className="brand-panel">
      <div className="brand">
        <Logo size={38} />
        <span>STRATIFYIQ</span>
      </div>
      <h1 className="login-title">Decide <span className="hero-accent">with confidence</span></h1>
      <p>Simulate every business decision, see its predicted impact, and act on the best option.</p>
      <ul className="brand-points">
        <li>Predict delay and budget risk before it happens</li>
        <li>Simulate hiring, budget and deadline changes</li>
        <li>Keep teams balanced, on time and on budget</li>
      </ul>
      <svg className="brand-chart" viewBox="0 0 400 140" preserveAspectRatio="xMidYMax meet" aria-hidden="true">
        {[[10, 80], [70, 110], [130, 60], [190, 100], [250, 40], [310, 90]].map(([x, h], i) => (
          <rect key={i} x={x} y={140 - h} width="40" height={h} fill={i === 4 ? "#FF6A13" : "#262626"} />
        ))}
        <polyline points="270,28 330,6" fill="none" stroke="#FF6A13" strokeWidth="2" />
      </svg>
    </aside>
  );
}
