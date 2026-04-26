import { useState } from "react";
import axios from "axios";

const API = "https://adolphvijay-talent-scout-api.hf.space";

// Design tokens
const C = {
  bg:        "#0f1117",
  surface:   "#1a1d27",
  surfaceHover: "#1f2235",
  border:    "#2a2d3e",
  accent:    "#6c63ff",
  accentHover:"#7c74ff",
  green:     "#22c55e",
  orange:    "#f59e0b",
  red:       "#ef4444",
  blue:      "#3b82f6",
  textPrimary:   "#f1f1f3",
  textSecondary: "#9094a6",
  textMuted:     "#5a5f72",
};

const styles = {
  badge: (color) => ({
    background: color + "22", color, border: `1px solid ${color}44`,
    borderRadius: 6, padding: "2px 10px", fontWeight: 700, fontSize: 13,
  }),
  tag: (color) => ({
    background: color + "18", color, border: `1px solid ${color}33`,
    borderRadius: 5, padding: "2px 8px", fontSize: 12,
  }),
  card: (highlight) => ({
    background: C.surface, borderRadius: 14, padding: 24, marginBottom: 16,
    border: highlight ? `1.5px solid ${C.accent}` : `1px solid ${C.border}`,
    boxShadow: highlight ? `0 0 24px ${C.accent}22` : "none",
    transition: "border 0.2s",
  }),
  btn: (disabled) => ({
    width: "100%", marginTop: 14, padding: "13px 28px",
    background: disabled ? C.border : C.accent,
    color: disabled ? C.textMuted : "#fff",
    border: "none", borderRadius: 10, fontSize: 15, fontWeight: 700,
    cursor: disabled ? "not-allowed" : "pointer",
    transition: "background 0.2s",
  }),
};

// Score bar 
const Bar = ({ value, color }) => (
  <div style={{ background: "#ffffff12", borderRadius: 6, height: 7, width: "100%", margin: "4px 0 12px" }}>
    <div style={{
      width: `${Math.min(value, 100)}%`, background: color,
      height: 7, borderRadius: 6, transition: "width 0.7s ease",
      boxShadow: `0 0 8px ${color}88`,
    }} />
  </div>
);

// Conversation modal 
const ConversationModal = ({ candidate, onClose }) => (
  <div style={{
    position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)",
    display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
    backdropFilter: "blur(4px)",
  }}>
    <div style={{
      background: C.surface, borderRadius: 18, padding: 32,
      maxWidth: 660, width: "92%", maxHeight: "82vh", overflowY: "auto",
      border: `1px solid ${C.border}`,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 22 }}>
        <h2 style={{ margin: 0, color: C.textPrimary, fontSize: 18 }}>
          💬 Conversation with {candidate.name}
        </h2>
        <button onClick={onClose} style={{
          border: "none", background: C.border, color: C.textPrimary,
          width: 32, height: 32, borderRadius: 8, fontSize: 16, cursor: "pointer",
        }}>✕</button>
      </div>

      {candidate.conversation.map((msg, i) => (
        <div key={i} style={{
          display: "flex",
          justifyContent: msg.role === "recruiter" ? "flex-start" : "flex-end",
          marginBottom: 14,
        }}>
          <div style={{
            maxWidth: "78%", borderRadius: 12, padding: "10px 14px",
            fontSize: 14, lineHeight: 1.6,
            background: msg.role === "recruiter" ? "#6c63ff18" : "#22c55e18",
            border: `1px solid ${msg.role === "recruiter" ? C.accent + "33" : C.green + "33"}`,
            color: C.textPrimary,
          }}>
            <div style={{
              fontWeight: 700, marginBottom: 5, fontSize: 12,
              color: msg.role === "recruiter" ? C.accent : C.green,
            }}>
              {msg.role === "recruiter" ? "🤵 Recruiter" : `👤 ${candidate.name.split(" ")[0]}`}
            </div>
            {msg.message}
          </div>
        </div>
      ))}

      <div style={{
        marginTop: 20, padding: 16, borderRadius: 12,
        background: "#f59e0b11", border: `1px solid ${C.orange}33`,
      }}>
        <div style={{ fontWeight: 700, color: C.orange, marginBottom: 8 }}>📊 Interest Analysis</div>
        <p style={{ margin: "0 0 8px", fontSize: 14, color: C.textPrimary }}>{candidate.interest_summary}</p>
        <div style={{ fontSize: 13, color: C.textSecondary }}>
          {candidate.positive_signals?.length > 0 &&
            <div style={{ color: C.green, marginBottom: 4 }}>✅ {candidate.positive_signals.join(" · ")}</div>}
          {candidate.negative_signals?.length > 0 &&
            <div style={{ color: C.red }}>⚠️ {candidate.negative_signals.join(" · ")}</div>}
        </div>
      </div>
    </div>
  </div>
);

// Candidate card
const CandidateCard = ({ candidate, rank }) => {
  const [showConvo, setShowConvo] = useState(false);

  const scoreColor = (s) => s >= 65 ? C.green : s >= 40 ? C.orange : C.red;
  const mc = scoreColor(candidate.match_score);
  const ic = scoreColor(candidate.interest_score);
  const cc = scoreColor(candidate.combined_score);

  return (
    <div style={styles.card(rank === 1)}>
      <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
        {rank === 1 && (
          <span style={styles.tag(C.accent)}>⭐ TOP MATCH</span>
        )}
        {candidate.id?.startsWith("uploaded") && (
          <span style={styles.tag(C.orange)}>📎 UPLOADED CV</span>
        )}
        {!candidate.open_to_work && (
          <span style={styles.tag(C.textMuted)}>⚪ Not actively looking</span>
        )}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 14 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 18, color: C.textPrimary }}>
            <span style={{ color: C.textMuted, fontWeight: 400 }}>#{rank} </span>
            {candidate.name}
          </h3>
          <div style={{ color: C.textSecondary, fontSize: 14, marginTop: 5 }}>
            {candidate.title} · {candidate.experience_years} yrs · {candidate.location}
          </div>
          {candidate.open_to_work && (
            <div style={{ fontSize: 13, color: C.green, marginTop: 4 }}>
              🟢 Open to work · Notice: {candidate.notice_period_days}d
            </div>
          )}
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          {[["MATCH", candidate.match_score, mc], ["INTEREST", candidate.interest_score, ic], ["COMBINED", candidate.combined_score, cc]].map(([label, val, col]) => (
            <div key={label} style={{ textAlign: "center" }}>
              <div style={{ fontSize: 10, color: C.textMuted, letterSpacing: 1, marginBottom: 4 }}>{label}</div>
              <span style={styles.badge(col)}>{val}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 18 }}>
        <div style={{ fontSize: 12, color: C.textMuted, marginBottom: 2 }}>Match Score</div>
        <Bar value={candidate.match_score} color={mc} />
        <div style={{ fontSize: 12, color: C.textMuted, marginBottom: 2 }}>Interest Score</div>
        <Bar value={candidate.interest_score} color={ic} />
      </div>

      <div style={{
        fontSize: 13, color: C.textSecondary, marginTop: 4,
        padding: "10px 14px", background: "#ffffff06", borderRadius: 8,
        borderLeft: `3px solid ${C.accent}`,
      }}>
        {candidate.match_explanation}
      </div>

      <div style={{ marginTop: 12, display: "flex", gap: 6, flexWrap: "wrap" }}>
        {candidate.matched_skills?.map(s => (
          <span key={s} style={styles.tag(C.green)}>✅ {s}</span>
        ))}
        {candidate.missing_skills?.map(s => (
          <span key={s} style={styles.tag(C.red)}>❌ {s}</span>
        ))}
      </div>

      <button onClick={() => setShowConvo(true)} style={{
        marginTop: 16, background: C.accent + "22", color: C.accent,
        border: `1px solid ${C.accent}44`, borderRadius: 8,
        padding: "8px 18px", cursor: "pointer", fontSize: 13, fontWeight: 600,
        transition: "background 0.2s",
      }}>
        💬 View Conversation
      </button>

      {showConvo && <ConversationModal candidate={candidate} onClose={() => setShowConvo(false)} />}
    </div>
  );
};

// Main App 
export default function App() {
  const [jd, setJd]           = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);
  const [error, setError]     = useState("");
  const [step, setStep]       = useState("");
  const [uploading, setUploading]     = useState(false);
  const [uploadMsg, setUploadMsg]     = useState("");
  const [uploadedNames, setUploadedNames] = useState([]);

  const steps = [
    "Parsing job description with AI...",
    "Searching candidates via RAG...",
    "Explaining skill matches...",
    "Simulating conversations...",
    "Scoring interest levels...",
    "Ranking shortlist...",
  ];

  const analyze = async () => {
    if (!jd.trim()) return;
    setLoading(true); setError(""); setResult(null);
    let i = 0; setStep(steps[0]);
    const iv = setInterval(() => { i = (i + 1) % steps.length; setStep(steps[i]); }, 3500);
    try {
      const res = await axios.post(`${API}/analyze`, { jd_text: jd, top_k: 5 });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Something went wrong. Is the backend running on port 8000?");
    } finally {
      clearInterval(iv); setLoading(false); setStep("");
    }
  };

  const uploadCV = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true); setUploadMsg("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await axios.post(`${API}/add-candidate`, form);
      setUploadMsg(`✅ ${res.data.candidate.name} added! Pool now has ${res.data.total_candidates} candidates.`);
      setUploadedNames(prev => [...prev, res.data.candidate.name]);
    } catch (e) {
      setUploadMsg(`❌ ${e.response?.data?.detail || "Upload failed"}`);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: C.bg, fontFamily: "system-ui, sans-serif", color: C.textPrimary }}>

      {/* Header */}
      <div style={{
        background: C.surface, borderBottom: `1px solid ${C.border}`,
        padding: "20px 32px", display: "flex", alignItems: "center", gap: 16,
      }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10,
          background: `linear-gradient(135deg, ${C.accent}, #a78bfa)`,
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20,
        }}>🎯</div>
        <div>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 800, color: C.textPrimary }}>
            AI Talent Scout
          </h1>
          <p style={{ margin: 0, fontSize: 13, color: C.textMuted }}>
            RAG-powered matching · Conversational interest scoring · Ranked shortlist
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "32px 16px" }}>

        {/* CV Upload */}
        <div style={{
          ...styles.card(false),
          border: `1px dashed ${C.accent}55`,
          background: C.accent + "08",
          marginBottom: 20,
        }}>
          <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 6, color: C.textPrimary }}>
            📎 Add Candidates via CV Upload
          </div>
          <div style={{ fontSize: 13, color: C.textSecondary, marginBottom: 14 }}>
            Upload a PDF or .txt resume — AI parses it and indexes it into the live candidate pool instantly.
          </div>
          <input
            type="file" accept=".pdf,.txt"
            onChange={uploadCV} disabled={uploading}
            style={{ fontSize: 13, color: C.textSecondary, cursor: "pointer" }}
          />
          {uploading && (
            <div style={{ marginTop: 10, fontSize: 13, color: C.accent }}>
              ⏳ Parsing CV with AI and indexing into FAISS...
            </div>
          )}
          {uploadMsg && (
            <div style={{
              marginTop: 10, fontSize: 13, fontWeight: 600,
              color: uploadMsg.startsWith("✅") ? C.green : C.red,
            }}>
              {uploadMsg}
            </div>
          )}
          {uploadedNames.length > 0 && (
            <div style={{ marginTop: 10, fontSize: 12, color: C.textMuted, display: "flex", gap: 6, flexWrap: "wrap" }}>
              <span>Added this session:</span>
              {uploadedNames.map(n => (
                <span key={n} style={styles.tag(C.orange)}>{n}</span>
              ))}
            </div>
          )}
        </div>

        {/* JD Input */}
        <div style={{ ...styles.card(false), marginBottom: 24 }}>
          <label style={{ fontWeight: 700, fontSize: 14, display: "block", marginBottom: 10, color: C.textPrimary }}>
            📋 Paste Job Description
          </label>
          <textarea
            value={jd}
            onChange={e => setJd(e.target.value)}
            placeholder={`We are hiring a Senior NLP Engineer...\n\nRequirements:\n- 4+ years experience\n- Python, PyTorch, HuggingFace Transformers\n- Experience with RAG pipelines and LLMs\n- Docker and AWS a plus`}
            style={{
              width: "100%", height: 190, borderRadius: 10,
              border: `1px solid ${C.border}`, background: C.bg,
              color: C.textPrimary, padding: 14, fontSize: 14,
              resize: "vertical", fontFamily: "inherit",
              boxSizing: "border-box", outline: "none",
              lineHeight: 1.6,
            }}
          />
          <button
            onClick={analyze}
            disabled={loading || !jd.trim()}
            style={styles.btn(loading || !jd.trim())}
          >
            {loading ? `⏳  ${step}` : "🚀  Find & Engage Candidates"}
          </button>
          {error && (
            <div style={{ marginTop: 12, color: C.red, fontSize: 13, padding: "10px 14px", background: C.red + "11", borderRadius: 8 }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Results */}
        {result && (
          <>
            {/* Parsed JD summary */}
            <div style={{ ...styles.card(false), marginBottom: 24 }}>
              <div style={{ fontWeight: 700, fontSize: 16, color: C.textPrimary, marginBottom: 12 }}>
                📌 {result.parsed_jd.role_title}
              </div>
              <div style={{ display: "flex", gap: 20, flexWrap: "wrap", fontSize: 14, color: C.textSecondary }}>
                <span>🎯 Seniority: <strong style={{ color: C.textPrimary }}>{result.parsed_jd.seniority}</strong></span>
                <span>📅 Min exp: <strong style={{ color: C.textPrimary }}>{result.parsed_jd.experience_years_min} yrs</strong></span>
                <span>✅ Required: <strong style={{ color: C.textPrimary }}>{result.parsed_jd.required_skills.join(", ")}</strong></span>
              </div>
              {result.parsed_jd.nice_to_have_skills?.length > 0 && (
                <div style={{ fontSize: 13, color: C.textMuted, marginTop: 8 }}>
                  Nice to have: {result.parsed_jd.nice_to_have_skills.join(", ")}
                </div>
              )}
            </div>

            {/* Ranked list header */}
            <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginBottom: 16 }}>
              <h2 style={{ margin: 0, color: C.textPrimary }}>🏆 Ranked Shortlist</h2>
              <span style={{ fontSize: 13, color: C.textMuted }}>
                {result.total_matched} candidates · 60% match + 40% interest
              </span>
            </div>

            {result.candidates.map((c, i) => (
              <CandidateCard key={c.id} candidate={c} rank={i + 1} />
            ))}
          </>
        )}
      </div>
    </div>
  );
}
