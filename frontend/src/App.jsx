import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("idle");
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("loading");
    setError(null);
    setAudioUrl(null);

    try {
      const res = await fetch(`${API_BASE}/api/narrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }

      const blob = await res.blob();
      setAudioUrl(URL.createObjectURL(blob));
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  return (
    <div style={{ maxWidth: 560, margin: "4rem auto", fontFamily: "sans-serif" }}>
      <h1>Narrated</h1>
      <p>Paste an article URL, get back a two-host podcast-style narration.</p>

      <form onSubmit={handleSubmit}>
        <input
          type="url"
          required
          placeholder="https://example.com/some-article"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
        />
        <button
          type="submit"
          disabled={status === "loading"}
          style={{ marginTop: "0.75rem", padding: "0.5rem 1rem" }}
        >
          {status === "loading" ? "Narrating..." : "Narrate"}
        </button>
      </form>

      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {audioUrl && (
        <audio controls src={audioUrl} style={{ marginTop: "1.5rem", width: "100%" }} />
      )}
    </div>
  );
}
