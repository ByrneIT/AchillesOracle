import { useState } from "react";
import { runScan } from "../api/client";
import ScoreBadge from "../components/ScoreBadge";
import IssueCard from "../components/IssueCard";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleScan() {
    if (!url) {
      setError("Please enter a URL to scan.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runScan(url);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Scan failed. Check the API server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1 className="site-title">AchillesOracle</h1>

      <div className="controls">
        <input
          className="input"
          type="text"
          placeholder="Enter URL (https://example.com)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleScan();
            }
          }}
        />

        <button className="btn" onClick={handleScan} disabled={loading}>
          {loading ? "Scanning…" : "Run Scan"}
        </button>
      </div>

      {error && (
        <p style={{ marginTop: "1rem", color: "var(--imperial-red)" }}>{error}</p>
      )}

      {result && (
        <div className="card">
          <div className="result-grid">
            <div style={{ flex: "0 0 320px" }}>
              <ScoreBadge score={result.score ?? 0} grade={result.grade ?? "-"} />
              <div style={{ marginTop: "0.6rem" }} className="meta">
                <div>
                  <strong>URL:</strong> {result.url}
                </div>
                <div style={{ marginTop: "0.4rem" }}>
                  Passed: <strong>{result.passed ?? 0}</strong> 
                  Warnings: <strong>{result.warnings ?? 0}</strong> 
                  Errors: <strong>{result.errors ?? 0}</strong>
                </div>
              </div>
            </div>

            <div style={{ flex: "1 1 540px" }}>
              <div className="issue-list">
                {Array.isArray(result.issues) && result.issues.length > 0 ? (
                  result.issues.map((iss, idx) => <IssueCard key={idx} issue={iss} />)
                ) : (
                  <p className="small-muted">No detailed issues returned.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}