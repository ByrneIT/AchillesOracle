import logo from "../assets/logo2.jpg";

export default function Header() {
  return (
    <header className="site-header">
      <div className="site-header__text">
        <h1>AchillesOracle</h1>
        <p>
          An intuitive website, domain, and webapp scanner built to highlight your
          security weaknesses and provide actionable insights to fortify your defenses.
        </p>
      </div>

      <div className="site-header__right">
        <span className="site-header__version">v0.1.0</span>
        <img
          src={logo}
          alt="AchillesOracle Logo"
          className="site-header__logo"
        />
      </div>
    </header>
  );
}
