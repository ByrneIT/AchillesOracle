import logo from "../assets/logo2.jpg";

export default function Header() {
  return (
    <header
      style={{
        padding: "1.5rem 2rem",
        borderBottom: "2px solid rgba(0,0,0,0.15)",
        background: "#f5f0e6", // light parchment tone to match the gold
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        minHeight: "180px"
      }}
    >
      {/* LEFT SIDE */}
      <div style={{ maxWidth: "55%" }}>
        <h1
          style={{
            margin: 0,
            fontFamily: "Cinzel, serif",
            color: "#1a3a5f", // deep blue from the logo
            fontSize: "2rem",
            textShadow: "0 0 4px rgba(0,0,0,0.15)"
          }}
        >
          AchillesOracle
        </h1>

        <p
          style={{
            margin: 0,
            marginTop: "0.35rem",
            color: "#4a4a4a",
            fontSize: "1rem",
            lineHeight: "1.4"
          }}
        >
          An intuitive website, domain, and webapp scanner built to highlight your
          security weaknesses and provide actionable insights to fortify your defenses.
        </p>
      </div>

      {/* RIGHT SIDE — VERSION + LOGO */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "1.5rem",
          marginLeft: "2rem"
        }}
      >
        <div
          style={{
            fontSize: "0.95rem",
            color: "#c49a2c", // gold from the logo
            fontWeight: "bold"
          }}
        >
          v0.1.0
        </div>

        <img
          src={logo}
          alt="AchillesOracle Logo"
          style={{
            height: "420px",
            minWidth: "620px",
            transform: "scale(1.05",
            objectFit: "contain",
            filter: "drop-shadow(0 0 6px rgba(0,0,0,0.25))",
            padding: "0 0.5rem"
          }}
        />
      </div>
    </header>
  );
}
