import { useState, useEffect } from "react";
import { Shield, RefreshCw, Code, Palette, Users, Target, Coffee } from "lucide-react";

const SLabel = ({ children }) => (
  <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 16 }}>
    {children}
  </div>
);

const COG_STATES = [
  { id: "CODING",     label: "Développement", color: "#60A5FA", Icon: Code,    apps: ["VSCode", "Terminal", "GitHub"], adapt: "Dark Pro · notifs OFF · focus max" },
  { id: "CREATIVE",   label: "Création",      color: "#F472B6", Icon: Palette, apps: ["Figma", "Adobe XD", "Procreate"], adapt: "Vibrant · flexibilité max · musique" },
  { id: "MEETING",    label: "Réunion",        color: "#34D399", Icon: Users,   apps: ["Zoom", "Teams", "Google Meet"], adapt: "Mode Pro · notes visibles · micro actif" },
  { id: "FOCUS",      label: "Focus Total",    color: "#A78BFA", Icon: Target,  apps: ["Notion", "Obsidian", "Word"], adapt: "Monochrome · tout caché · DND absolu" },
  { id: "RELAXATION", label: "Détente",        color: "#FBBF24", Icon: Coffee,  apps: ["YouTube", "Spotify", "Netflix"], adapt: "Warm · entertainment · notifs soft" },
];

function Cognitive({ ambientUpdate, eyeGaze, connected, ambientConnected, eyeConnected }) {
  const [active, setActive] = useState("FOCUS");
  const [manualOverride, setManualOverride] = useState(false);
  const current = COG_STATES.find(s => s.id === active) || COG_STATES[3];

  useEffect(() => {
    if (manualOverride || !ambientUpdate?.cognitive_state) return;
    const candidate = ambientUpdate.cognitive_state.toString().toUpperCase();
    if (COG_STATES.some(s => s.id === candidate)) {
      setActive(candidate);
    }
  }, [ambientUpdate, manualOverride]);

  const detectedState = ambientUpdate?.cognitive_state
    ? ambientUpdate.cognitive_state.toString().toUpperCase()
    : "N/A";
  const detectedApps = Array.isArray(ambientUpdate?.detected_apps) && ambientUpdate.detected_apps.length > 0
    ? ambientUpdate.detected_apps
    : (ambientUpdate?.foreground_app ? [ambientUpdate.foreground_app] : []);
  const confidencePct = Math.round((ambientUpdate?.confidence ?? 0) * 100);
  const gazePosition = eyeGaze ? `x:${Math.round(eyeGaze.x ?? 0)} y:${Math.round(eyeGaze.y ?? 0)}${eyeGaze.z != null ? ` z:${Math.round(eyeGaze.z)}` : ''}` : "Aucun flux";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ animation: "fadeUp .35s ease both" }}>
        <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 8 }}>Liquid OS · Adaptation cognitive</div>
        <h1 style={{ fontSize: 28, fontWeight: 600, color: "#E2E8F0", letterSpacing: "-0.02em" }}>Cognitif</h1>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 12 }}>
          {[
            { label: "FastAPI", active: connected, color: connected ? "#10B981" : "#EF4444", value: connected ? "Connecté" : "Hors ligne" },
            { label: "Ambient", active: ambientConnected, color: ambientConnected ? "#10B981" : "#F59E0B", value: ambientConnected ? "Flux actif" : "En attente" },
            { label: "Eye", active: eyeConnected, color: eyeConnected ? "#10B981" : "#F59E0B", value: eyeConnected ? "Tracking actif" : "En attente" },
          ].map(({ label, active, color, value }) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 14px", borderRadius: 12, background: active ? `${color}15` : "rgba(255,255,255,.05)", border: `1px solid ${active ? `${color}30` : "rgba(255,255,255,.08)"}`, color: active ? color : "rgba(226,232,240,.55)", fontSize: 12 }}>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: color }} />
              <strong>{label}:</strong> {value}
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        {COG_STATES.map(({ id, label, color, Icon }) => {
          const on = id === active;
          return (
            <div
              key={id}
              className={`cog-btn${on ? " active" : ""}`}
              onClick={() => { setManualOverride(true); setActive(id); }}
              style={on ? { borderColor: color, background: `${color}12` } : {}}
            >
              <div style={{
                width: 36, height: 36, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
                background: on ? `${color}20` : "rgba(255,255,255,.04)",
                border: `1px solid ${on ? color + "44" : "rgba(255,255,255,.06)"}`,
                transition: "all .2s"
              }}>
                <Icon size={16} color={on ? color : "rgba(226,232,240,.35)"} strokeWidth={1.5} />
              </div>
              <span style={{ fontSize: 11, color: on ? color : "rgba(226,232,240,.4)", fontWeight: on ? 500 : 400, textAlign: "center" }}>{label}</span>
            </div>
          );
        })}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, flex: 1 }}>
        <div className="glass" style={{ padding: 28, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 20 }}>
          <div style={{ position: "relative", width: 140, height: 140 }}>
            <svg viewBox="0 0 140 140" style={{ width: 140, height: 140, position: "absolute", inset: 0 }}>
              <circle cx="70" cy="70" r="58" fill="none" stroke="rgba(255,255,255,.05)" strokeWidth="8" />
              <circle
                cx="70" cy="70" r="58" fill="none"
                stroke={current.color}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 58 * 0.72} ${2 * Math.PI * 58}`}
                style={{ transform: "rotate(-90deg)", transformOrigin: "70px 70px", filter: `drop-shadow(0 0 6px ${current.color}66)`, transition: "stroke .4s ease, filter .4s ease" }}
              />
            </svg>
            <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 4 }}>
              <current.Icon size={24} color={current.color} strokeWidth={1.5} />
              <span style={{ fontSize: 11, color: current.color, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", transition: "color .3s" }}>{current.id}</span>
            </div>
          </div>

          <div style={{ width: "100%", textAlign: "center" }}>
            <div style={{ fontSize: 11, color: "rgba(226,232,240,.3)", marginBottom: 8 }}>Confiance détection</div>
            <div style={{ height: 6, borderRadius: 3, background: "rgba(255,255,255,.06)", overflow: "hidden" }}>
              <div style={{
                height: "100%", borderRadius: 3, width: `${Math.max(confidencePct, 4)}%`,
                background: `linear-gradient(90deg, ${current.color}88, ${current.color})`,
                transition: "width .4s ease, background .4s ease",
                boxShadow: `0 0 8px ${current.color}44`
              }} />
            </div>
            <div style={{ fontSize: 12, color: current.color, marginTop: 6, fontFamily: "monospace", fontWeight: 600, transition: "color .3s" }}>{confidencePct}%</div>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="glass" style={{ padding: 22, flex: 1 }}>
            <SLabel>Fenêtre active (temps réel)</SLabel>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {detectedApps.length > 0 ? detectedApps.map(app => (
                <div key={app} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", borderRadius: 10, background: "rgba(255,255,255,.03)", border: "1px solid rgba(255,255,255,.05)" }}>
                  <div style={{ width: 7, height: 7, borderRadius: "50%", background: current.color, boxShadow: `0 0 6px ${current.color}66` }} />
                  <span style={{ fontSize: 13, color: "rgba(226,232,240,.65)" }}>{app}</span>
                </div>
              )) : (
                <div style={{ fontSize: 12, color: "rgba(226,232,240,.4)", padding: "8px 0" }}>
                  Aucune fenêtre détectée — placez l'app à analyser au premier plan.
                </div>
              )}
            </div>
            <div style={{ marginTop: 12, fontSize: 11, color: "rgba(226,232,240,.32)", lineHeight: 1.5 }}>
              Profil « {current.label} » : {current.apps.join(", ")} (exemples, pas vos apps ouvertes).
            </div>
            <div style={{ marginTop: 16, padding: 14, borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.06)" }}>
              <div style={{ fontSize: 11, color: "rgba(226,232,240,.4)", marginBottom: 8 }}>Détection en direct</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                <div style={{ fontSize: 13, color: "rgba(226,232,240,.75)" }}><strong>État</strong><br />{detectedState}</div>
                <div style={{ fontSize: 13, color: "rgba(226,232,240,.75)" }}><strong>Gaze</strong><br />{gazePosition}</div>
              </div>
            </div>
          </div>
          <div className="glass" style={{ padding: 22, flex: 1 }}>
            <SLabel>Adaptations appliquées</SLabel>
            <div style={{ padding: "12px 16px", borderRadius: 12, background: `${current.color}0d`, border: `1px solid ${current.color}22`, transition: "all .3s" }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                <Shield size={14} color={current.color} strokeWidth={1.5} style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ fontSize: 13, color: "rgba(226,232,240,.7)", lineHeight: 1.5 }}>{current.adapt}</span>
              </div>
            </div>
            <div style={{ marginTop: 14 }}>
              <button
                className="btn primary"
                style={{ width: "100%", justifyContent: "center" }}
                onClick={() => {
                  if (ambientUpdate?.cognitive_state) {
                    setManualOverride(false);
                    setActive(ambientUpdate.cognitive_state.toString().toUpperCase());
                  }
                }}
                disabled={!ambientUpdate?.cognitive_state}
              >
                <RefreshCw size={12} strokeWidth={1.5} /> Suivre la détection auto
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Cognitive;
