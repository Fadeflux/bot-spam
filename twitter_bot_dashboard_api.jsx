import { useState, useRef, useCallback, useEffect } from "react";

// ─── Fonts ───────────────────────────────────────────────
const style = document.createElement("style");
style.textContent = `
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --border: #2a2a3a;
    --accent: #00e5ff;
    --accent2: #7c3aed;
    --accent3: #f59e0b;
    --red: #ef4444;
    --green: #22c55e;
    --text: #e2e8f0;
    --muted: #64748b;
    --font-mono: 'Space Mono', monospace;
    --font-display: 'Syne', sans-serif;
  }

  body { background: var(--bg); color: var(--text); font-family: var(--font-display); }

  .glow-cyan { box-shadow: 0 0 20px rgba(0,229,255,0.15); }
  .glow-purple { box-shadow: 0 0 20px rgba(124,58,237,0.2); }

  @keyframes pulse-glow {
    0%,100% { box-shadow: 0 0 6px rgba(0,229,255,0.4); }
    50% { box-shadow: 0 0 18px rgba(0,229,255,0.8), 0 0 30px rgba(0,229,255,0.3); }
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes fadeUp {
    from { opacity:0; transform: translateY(12px); }
    to   { opacity:1; transform: translateY(0); }
  }
  @keyframes slideIn {
    from { opacity:0; transform: translateX(-8px); }
    to   { opacity:1; transform: translateX(0); }
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

  .fade-up { animation: fadeUp 0.35s ease forwards; }
  .slide-in { animation: slideIn 0.3s ease forwards; }
  .blink { animation: blink 1.2s infinite; }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: var(--surface); }
  ::-webkit-scrollbar-thumb { background: var(--accent2); border-radius: 4px; }

  textarea, input {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  textarea:focus, input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(0,229,255,0.1);
  }

  .checkbox-custom {
    appearance: none;
    width: 18px; height: 18px;
    border: 2px solid var(--border);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
    position: relative;
  }
  .checkbox-custom:checked {
    background: var(--accent2);
    border-color: var(--accent2);
  }
  .checkbox-custom:checked::after {
    content: '✓';
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 11px;
    font-weight: bold;
  }

  .btn {
    font-family: var(--font-display);
    font-weight: 700;
    letter-spacing: 0.05em;
    cursor: pointer;
    border: none;
    border-radius: 8px;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .btn:hover { transform: translateY(-1px); }
  .btn:active { transform: translateY(0); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

  .btn-primary {
    background: linear-gradient(135deg, var(--accent2), #5b21b6);
    color: #fff;
    padding: 12px 24px;
    font-size: 14px;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
  }
  .btn-primary:hover { box-shadow: 0 6px 28px rgba(124,58,237,0.6); }

  .btn-danger {
    background: linear-gradient(135deg, var(--red), #b91c1c);
    color: #fff;
    padding: 12px 24px;
    font-size: 14px;
    box-shadow: 0 4px 16px rgba(239,68,68,0.3);
  }
  .btn-sm {
    padding: 7px 14px;
    font-size: 12px;
    border-radius: 6px;
    background: var(--surface2);
    color: var(--accent);
    border: 1px solid var(--accent);
  }
  .btn-sm:hover { background: rgba(0,229,255,0.08); }

  .tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: var(--font-mono);
    font-weight: 700;
    letter-spacing: 0.08em;
  }
  .tag-sim { background: rgba(245,158,11,0.15); color: var(--accent3); border: 1px solid rgba(245,158,11,0.3); }
  .tag-real { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(239,68,68,0.3); }
  .tag-ok { background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid rgba(34,197,94,0.3); }

  .log-entry {
    padding: 6px 10px;
    border-radius: 6px;
    font-family: var(--font-mono);
    font-size: 12px;
    line-height: 1.5;
    border-left: 2px solid transparent;
  }
  .log-ok { background: rgba(34,197,94,0.06); border-color: var(--green); color: #86efac; }
  .log-err { background: rgba(239,68,68,0.06); border-color: var(--red); color: #fca5a5; }
  .log-info { background: rgba(0,229,255,0.06); border-color: var(--accent); color: #67e8f9; }
  .log-warn { background: rgba(245,158,11,0.06); border-color: var(--accent3); color: #fcd34d; }

  .section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
  }
  .section-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.02);
  }
  .section-title {
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
  }
  .section-body { padding: 20px; }

  .stat-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
  }
  .stat-val {
    font-family: var(--font-mono);
    font-size: 28px;
    font-weight: 700;
    color: var(--accent);
  }
  .stat-label {
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
  }

  .progress-bar {
    height: 4px;
    background: var(--surface2);
    border-radius: 4px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
    transition: width 0.4s ease;
  }

  .account-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--surface2);
    transition: all 0.2s;
    cursor: pointer;
  }
  .account-row:hover { border-color: var(--accent2); background: rgba(124,58,237,0.08); }
  .account-row.selected { border-color: var(--accent2); background: rgba(124,58,237,0.12); animation: pulse-glow 2s infinite; }

  .avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800;
    font-family: var(--font-display);
    flex-shrink: 0;
  }

  .spinner {
    width: 16px; height: 16px;
    border: 2px solid rgba(0,229,255,0.2);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }

  .terminal-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    animation: pulse-glow 2s infinite;
    flex-shrink: 0;
  }
`;
document.head.appendChild(style);

// ─── Helpers ─────────────────────────────────────────────
const API_URL = "http://localhost:5000";
const pick = arr => arr[Math.floor(Math.random() * arr.length)];
const extractId  = url => { const m = url.match(/(?:twitter|x)\.com\/\w+\/status\/(\d+)/); return m ? m[1] : null; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const ts = () => new Date().toLocaleTimeString("fr-FR", { hour12: false });

// ─── API Calls ───────────────────────────────────────────
const apiCall = async (endpoint, method = "GET", body = null) => {
  try {
    const options = {
      method,
      headers: { "Content-Type": "application/json" }
    };
    if (body) options.body = JSON.stringify(body);
    
    const res = await fetch(`${API_URL}${endpoint}`, options);
    if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
    return await res.json();
  } catch (e) {
    throw new Error(`API Error: ${e.message}`);
  }
};

// ─── Main App ─────────────────────────────────────────────
export default function App() {
  // ── State ──
  const [tab, setTab] = useState("accounts");
  const [accounts, setAccounts] = useState([]);
  const [newForm, setNewForm] = useState({ key: "", secret: "", token: "", tokenSecret: "" });
  const [adding, setAdding] = useState(false);
  const [links, setLinks] = useState("");
  const [nbComments, setNbComments] = useState(1);
  const [delay, setDelay] = useState(5);
  const [mode, setMode] = useState("sim");
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState(0);
  const [apiConnected, setApiConnected] = useState(false);
  const logsEndRef = useRef(null);

  // ── Init API connection ──
  useEffect(() => {
    const checkApi = async () => {
      try {
        await apiCall("/api/health");
        setApiConnected(true);
        loadAccounts();
        pollStatus();
      } catch (e) {
        console.error("API not connected:", e);
        setApiConnected(false);
      }
    };
    checkApi();
  }, []);

  // ── Auto-scroll logs ──
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // ── Load accounts ──
  const loadAccounts = async () => {
    try {
      const res = await apiCall("/api/accounts");
      if (res.success) {
        const formattedAccounts = res.accounts.map((acc, i) => ({
          id: acc.id,
          name: acc.name,
          username: `compte_${acc.id}`,
          checked: false,
          comments: 0,
          status: "idle",
          color: ["#7c3aed","#06b6d4","#f59e0b","#ec4899","#22c55e","#f97316","#8b5cf6","#14b8a6"][i % 8]
        }));
        setAccounts(formattedAccounts);
      }
    } catch (e) {
      console.error("Failed to load accounts:", e);
    }
  };

  // ── Poll status while running ──
  const pollStatus = async () => {
    try {
      const res = await apiCall("/api/status");
      setRunning(res.running);
      setProgress(res.progress);
    } catch (e) {
      console.error("Poll error:", e);
    }
    
    setTimeout(pollStatus, 1000);
  };

  const selected = accounts.filter(a => a.checked);

  const toggleAccount = id => {
    setAccounts(a => a.map(acc => acc.id === id ? { ...acc, checked: !acc.checked } : acc));
  };

  const toggleAll = () => {
    const allChecked = accounts.every(a => a.checked);
    setAccounts(a => a.map(acc => ({ ...acc, checked: !allChecked })));
  };

  const addLog = useCallback((msg, type = "info") => {
    setLogs(l => [...l, { msg, type, time: ts() }]);
  }, []);

  const addAccount = async () => {
    if (!newForm.key || !newForm.secret || !newForm.token || !newForm.tokenSecret) {
      addLog("Tous les champs sont requis", "err");
      return;
    }
    setAdding(true);
    
    try {
      const res = await apiCall("/api/accounts/add", "POST", {
        api_key: newForm.key,
        api_secret: newForm.secret,
        access_token: newForm.token,
        access_token_secret: newForm.tokenSecret
      });
      
      if (res.success) {
        addLog(`✅ Compte ${res.account_id} ajouté`, "ok");
        setNewForm({ key: "", secret: "", token: "", tokenSecret: "" });
        loadAccounts();
        setTab("run");
      } else {
        addLog(`❌ ${res.error}`, "err");
      }
    } catch (e) {
      addLog(`❌ Erreur: ${e.message}`, "err");
    }
    
    setAdding(false);
  };

  const removeAccount = async (id) => {
    try {
      const res = await apiCall(`/api/accounts/${id}`, "DELETE");
      if (res.success) {
        addLog(`✅ Compte ${id} supprimé`, "ok");
        loadAccounts();
      } else {
        addLog(`❌ ${res.error}`, "err");
      }
    } catch (e) {
      addLog(`❌ Erreur: ${e.message}`, "err");
    }
  };

  const validLinks = links.split("\n").map(l => l.trim()).filter(l => l.startsWith("http"));

  const launch = async () => {
    if (selected.length === 0) { addLog("Sélectionnez au moins un compte", "err"); return; }
    if (validLinks.length === 0) { addLog("Aucun lien valide", "err"); return; }

    try {
      setLogs([]);
      const res = await apiCall("/api/launch", "POST", {
        account_ids: selected.map(a => a.id),
        links: validLinks,
        nb_comments: nbComments,
        delay: delay,
        mode: mode
      });

      if (res.success) {
        addLog(`🚀 Lancement — ${res.accounts} compte(s), ${res.links} tweet(s)`, "info");
        addLog(`Mode: ${mode === "real" ? "🔴 RÉEL" : "🟡 SIMULATION"}`, mode === "real" ? "err" : "warn");
        setTab("monitor");
      } else {
        addLog(`❌ ${res.error}`, "err");
      }
    } catch (e) {
      addLog(`❌ Erreur: ${e.message}`, "err");
    }
  };

  const stop = async () => {
    try {
      const res = await apiCall("/api/stop", "POST");
      if (res.success) {
        addLog("⛔ Arrêt demandé", "warn");
      }
    } catch (e) {
      addLog(`❌ Erreur: ${e.message}`, "err");
    }
  };

  // ─────────────────────── UI ───────────────────────────
  if (!apiConnected) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--bg)", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ marginBottom: 16 }}>
            <div className="spinner" style={{ width: 28, height: 28, margin: "0 auto" }} />
          </div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: 18, marginBottom: 8 }}>Connexion API...</h2>
          <p style={{ color: "var(--muted)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
            Assurez-vous que le serveur Flask est lancé sur http://localhost:5000
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", padding: "24px", maxWidth: 920, margin: "0 auto" }}>
      
      {/* Header */}
      <div style={{ marginBottom: 28, display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--green)", boxShadow: "0 0 10px var(--green)" }} className="blink" />
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--green)", letterSpacing: "0.15em" }}>🔗 API CONNECTÉE</span>
          </div>
          <h1 style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 26, letterSpacing: "-0.02em", lineHeight: 1 }}>
            Comment<span style={{ color: "var(--accent2)" }}>Bot</span>
          </h1>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {["accounts","run","monitor"].map(t => (
            <button key={t} className="btn btn-sm" onClick={() => setTab(t)}
              style={tab === t ? { background: "var(--accent2)", borderColor: "var(--accent2)", color: "#fff" } : {}}>
              {{ accounts: "👤 Comptes", run: "⚙️ Lancement", monitor: "📊 Monitor" }[t]}
            </button>
          ))}
        </div>
      </div>

      {/* ─── TAB: ACCOUNTS ─── */}
      {tab === "accounts" && (
        <div className="fade-up" style={{ display: "grid", gap: 16 }}>
          
          {/* Existing accounts */}
          {accounts.length > 0 && (
            <div className="section-card">
              <div className="section-header" style={{ justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent)" }} />
                  <span className="section-title">Comptes connectés</span>
                  <span className="tag tag-ok">{accounts.length}</span>
                </div>
                <button className="btn btn-sm" onClick={toggleAll} style={{ fontSize: 11 }}>
                  {accounts.every(a => a.checked) ? "Tout désélectionner" : "Tout sélectionner"}
                </button>
              </div>
              <div className="section-body" style={{ display: "grid", gap: 8 }}>
                {accounts.map((acc, i) => (
                  <div key={acc.id} className={`account-row${acc.checked ? " selected" : ""}`}
                    onClick={() => toggleAccount(acc.id)}
                    style={{ animationDelay: `${i * 0.05}s` }}>
                    <input type="checkbox" className="checkbox-custom" checked={acc.checked} readOnly />
                    <div className="avatar" style={{ background: acc.color + "22", color: acc.color, border: `2px solid ${acc.color}44` }}>
                      {acc.name[0]}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 700, fontSize: 14 }}>{acc.name}</div>
                      <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--muted)" }}>@{acc.username}</div>
                    </div>
                    <button className="btn" onClick={e => { e.stopPropagation(); removeAccount(acc.id); }}
                      style={{ padding: "4px 8px", background: "transparent", color: "var(--red)", fontSize: 16, borderRadius: 6 }}>
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Add new account */}
          <div className="section-card">
            <div className="section-header">
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent2)" }} />
              <span className="section-title">Ajouter un compte</span>
            </div>
            <div className="section-body">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
                {[
                  ["API Key", "key", "API_KEY"],
                  ["API Secret", "secret", "API_SECRET"],
                  ["Access Token", "token", "ACCESS_TOKEN"],
                  ["Access Token Secret", "tokenSecret", "ACCESS_TOKEN_SECRET"]
                ].map(([label, field, ph]) => (
                  <div key={field}>
                    <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 5, fontFamily: "var(--font-mono)" }}>{label}</div>
                    <input
                      type="password"
                      placeholder={ph}
                      value={newForm[field]}
                      onChange={e => setNewForm(f => ({ ...f, [field]: e.target.value }))}
                      style={{ width: "100%", padding: "9px 12px", borderRadius: 8 }}
                    />
                  </div>
                ))}
              </div>
              <div style={{ display: "flex", gap: 10, alignItems: "center", marginTop: 4 }}>
                <button className="btn btn-primary" onClick={addAccount} disabled={adding}>
                  {adding ? <><div className="spinner" /> Connexion...</> : <><span>⚡</span> Connecter le compte</>}
                </button>
                <span style={{ fontSize: 12, color: "var(--muted)", fontFamily: "var(--font-mono)" }}>
                  OAuth 1.0a — Tokens sauvegardés sur serveur
                </span>
              </div>
            </div>
          </div>

          {accounts.length > 0 && (
            <button className="btn btn-primary" onClick={() => setTab("run")} style={{ alignSelf: "flex-start" }}>
              Configurer le lancement →
            </button>
          )}
        </div>
      )}

      {/* ─── TAB: RUN ─── */}
      {tab === "run" && (
        <div className="fade-up" style={{ display: "grid", gap: 16 }}>

          {/* Selected accounts summary */}
          <div className="section-card">
            <div className="section-header">
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent)" }} />
              <span className="section-title">Comptes sélectionnés</span>
              <span className="tag tag-ok">{selected.length}/{accounts.length}</span>
              <button className="btn btn-sm" onClick={() => setTab("accounts")} style={{ marginLeft: "auto", fontSize: 11 }}>
                ← Modifier
              </button>
            </div>
            <div className="section-body" style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {selected.length === 0 && (
                <div style={{ color: "var(--muted)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                  Aucun compte sélectionné — allez dans "Comptes"
                </div>
              )}
              {selected.map(acc => (
                <div key={acc.id} style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 20, background: acc.color + "18", border: `1px solid ${acc.color}44`, fontSize: 13 }}>
                  <div style={{ width: 7, height: 7, borderRadius: "50%", background: acc.color }} />
                  @{acc.username}
                </div>
              ))}
            </div>
          </div>

          {/* Links */}
          <div className="section-card">
            <div className="section-header">
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent3)" }} />
              <span className="section-title">Tweets cibles</span>
              {validLinks.length > 0 && <span className="tag tag-ok">{validLinks.length} lien(s)</span>}
            </div>
            <div className="section-body">
              <textarea
                placeholder={"https://x.com/user/status/1234567890\nhttps://x.com/user/status/0987654321\n..."}
                value={links}
                onChange={e => setLinks(e.target.value)}
                style={{ width: "100%", height: 120, padding: 12, borderRadius: 8, resize: "vertical", lineHeight: 1.7 }}
              />
              <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 6 }}>
                Un lien par ligne — formats twitter.com et x.com supportés
              </div>
            </div>
          </div>

          {/* Params */}
          <div className="section-card">
            <div className="section-header">
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent2)" }} />
              <span className="section-title">Paramètres</span>
            </div>
            <div className="section-body" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
              <div>
                <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 5, fontFamily: "var(--font-mono)" }}>
                  Commentaires / tweet
                </div>
                <input
                  type="number"
                  min="1"
                  value={nbComments}
                  onChange={e => setNbComments(Math.max(1, parseInt(e.target.value) || 1))}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 8 }}
                />
              </div>
              <div>
                <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 5, fontFamily: "var(--font-mono)" }}>Délai (secondes)</div>
                <input
                  type="number"
                  min="1"
                  value={delay}
                  onChange={e => setDelay(Math.max(1, parseInt(e.target.value) || 5))}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 8 }}
                />
              </div>
              <div>
                <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 5, fontFamily: "var(--font-mono)" }}>Mode</div>
                <select
                  value={mode}
                  onChange={e => setMode(e.target.value)}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 8, background: "var(--surface2)", border: "1px solid var(--border)", color: "var(--text)", fontFamily: "var(--font-mono)", fontSize: 13, outline: "none", cursor: "pointer" }}
                >
                  <option value="sim">🟡 Simulation</option>
                  <option value="real">🔴 Mode Réel</option>
                </select>
              </div>
            </div>

            {/* Summary */}
            {selected.length > 0 && validLinks.length > 0 && (
              <div style={{ marginTop: 16, padding: 14, background: "var(--surface2)", borderRadius: 10, border: "1px solid var(--border)" }}>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--muted)", marginBottom: 8 }}>RÉSUMÉ</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                  {[
                    ["Comptes", selected.length],
                    ["Tweets", validLinks.length],
                    ["Total commentaires", selected.length * validLinks.length * nbComments]
                  ].map(([label, val]) => (
                    <div key={label} style={{ textAlign: "center" }}>
                      <div style={{ fontFamily: "var(--font-mono)", fontSize: 22, fontWeight: 700, color: "var(--accent)" }}>{val}</div>
                      <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2 }}>{label}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div style={{ display: "flex", gap: 12 }}>
            {!running ? (
              <button className="btn btn-primary" onClick={launch} disabled={selected.length === 0 || validLinks.length === 0}>
                <span>🚀</span>
                {mode === "real" ? "LANCER (RÉEL)" : "LANCER (SIMULATION)"}
              </button>
            ) : (
              <button className="btn btn-danger" onClick={stop}>
                <span>⛔</span> Arrêter
              </button>
            )}
            {running && (
              <button className="btn btn-sm" onClick={() => setTab("monitor")}>
                Voir le monitor →
              </button>
            )}
          </div>
        </div>
      )}

      {/* ─── TAB: MONITOR ─── */}
      {tab === "monitor" && (
        <div className="fade-up" style={{ display: "grid", gap: 16 }}>

          {/* Stats row */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
            {[
              ["Logs", logs.length, "💬"],
              ["Comptes", selected.length, "👤"],
              ["Progression", `${progress}%`, "📊"],
              ["Statut", running ? "EN COURS" : "TERMINÉ", running ? "🟢" : "⚪"]
            ].map(([label, val, icon]) => (
              <div key={label} className="stat-card">
                <div style={{ fontSize: 18, marginBottom: 4 }}>{icon}</div>
                <div className="stat-val" style={{ fontSize: 20 }}>{val}</div>
                <div className="stat-label">{label}</div>
              </div>
            ))}
          </div>

          {/* Progress bar */}
          {(running || progress > 0) && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--muted)", fontFamily: "var(--font-mono)", marginBottom: 6 }}>
                <span>Progression globale</span><span>{progress}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }} />
              </div>
            </div>
          )}

          {/* Log terminal */}
          <div className="section-card">
            <div className="section-header" style={{ justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div className="terminal-dot" style={{ background: "var(--green)" }} />
                <span className="section-title">Terminal</span>
              </div>
              <button className="btn btn-sm" onClick={() => setLogs([])} style={{ fontSize: 11 }}>
                Effacer
              </button>
            </div>
            <div style={{ padding: "12px 16px", maxHeight: 320, overflowY: "auto", display: "grid", gap: 4 }}>
              {logs.length === 0 && (
                <div style={{ color: "var(--muted)", fontFamily: "var(--font-mono)", fontSize: 12, padding: 8 }}>
                  En attente de lancement...
                </div>
              )}
              {logs.map((log, i) => (
                <div key={i} className={`log-entry log-${log.type} slide-in`}>
                  <span style={{ color: "var(--muted)", marginRight: 8 }}>{log.time}</span>
                  {log.msg}
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>

          {!running && logs.length === 0 && (
            <button className="btn btn-primary" onClick={() => setTab("run")} style={{ alignSelf: "flex-start" }}>
              ← Configurer et lancer
            </button>
          )}
        </div>
      )}
    </div>
  );
}
