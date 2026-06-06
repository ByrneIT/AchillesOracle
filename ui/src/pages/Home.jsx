import { useState } from "react";
import { runScan } from "../api/client";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleScan() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runScan(url);
      setResult(data);
    } catch (err) {
      setError("Scan failed. Check the API server.");
    }

    setLoading(false);
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ fontFamily: "Cinzel, serif", color: "var(--aegean)" }}>
        AchillesOracle
      </h1>

      <div style={{ marginTop: "1rem" }}>
        <input
          type="text"
          placeholder="Enter URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{
            width: "300px",
            padding: "8px",
            border: "1px solid var(--slate)",
            borderRadius: "4px"
          }}
        />

        <button
          onClick={handleScan}
          style={{
            marginLeft: "1rem",
            padding: "8px 16px",
            background: "var(--aegean)",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Run Scan
        </button>
      </div>

      {loading && (
        <p style={{ marginTop: "1.5rem", color: "var(--slate)" }}>
          Running scan...
        </p>
      )}

      {error && (
        <p style={{ marginTop: "1.5rem", color: "var(--imperial-red)" }}>
          {error}
        </p>
      )}

      {result && (
        <pre
          style={{
            marginTop: "2rem",
            padding: "1rem",
            background: "white",
            borderRadius: "6px",
            border: "1px solid var(--slate)",
            overflowX: "auto"
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}