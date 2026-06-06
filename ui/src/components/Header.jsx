export default function Header() {
  return (
    <header
      style={{
        padding: "1rem 2rem",
        borderBottom: "1px solid var(--slate)",
        background: "var(--marble)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}
    >
      <div>
        <h1
          style={{
            margin: 0,
            fontFamily: "Cinzel, serif",
            color: "var(--aegean)",
            fontSize: "1.8rem"
          }}
        >
          AchillesOracle
        </h1>
        <p
          style={{
            margin: 0,
            marginTop: "0.25rem",
            color: "var(--slate)",
            fontSize: "0.9rem"
          }}
        >
          Greco‑Roman security insight for modern web apps
        </p>
      </div>

      <div
        style={{
          fontSize: "0.85rem",
          color: "var(--slate)"
        }}
      >
        v0.1.0
      </div>
    </header>
  );
}
