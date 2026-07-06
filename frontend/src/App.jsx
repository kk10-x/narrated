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
    <div className="page">
      <div className="brand">
        <div className="brand-mark">🎙️</div>
        <h1>Narrated</h1>
      </div>
      <p className="subtitle">
        Paste an article URL and get back a short, two-host podcast-style discussion of it —
        not flat text-to-speech.
      </p>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <input
            type="url"
            required
            placeholder="https://example.com/some-article"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button type="submit" disabled={status === "loading"}>
            {status === "loading" ? (
              <>
                <span className="spinner" />
                Narrating
              </>
            ) : (
              "Narrate"
            )}
          </button>
        </form>

        {error && <div className="error-box">{error}</div>}

        {audioUrl && (
          <div className="result">
            <div className="result-label">Your narration</div>
            <audio controls src={audioUrl} />
          </div>
        )}
      </div>

      <p className="how-it-works">
        <strong>How it works:</strong> the article is scraped and condensed into a two-host
        dialogue by Claude, then rendered as audio with two distinct ElevenLabs voices.
      </p>
    </div>
  );
}
