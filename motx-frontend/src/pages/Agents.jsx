import { useState, useEffect } from "react";
import { Database, Eye, Mic, Scan, RotateCcw, Bot } from "lucide-react";

// Dictionnaire pour mapper les chaînes d'icônes à des composants Lucide réels
const ICON_MAP = {
  Database: Database,
  Eye: Eye,
  Mic: Mic,
  Scan: Scan,
  RotateCcw: RotateCcw,
};

function Agents({ agents, onToggleAgent, addToast }) {
  const [demoAgent, setDemoAgent] = useState(null);
  const activeCount = agents.filter(a => a.active).length;

  useEffect(() => {
    if (!demoAgent) return;
    const timer = setTimeout(() => setDemoAgent(null), 22000);
    return () => clearTimeout(timer);
  }, [demoAgent]);

  const demoConfigs = {
    eyetrack: {
      label: "Eye Tracking",
      bullets: [
        "Regard simulé sur l'UI : barre d'outils → éditeur → panneau terminal",
        "Carte de gaze en temps réel",
        "Détection de point d'intérêt activée",
      ],
      description: "Simulation de suivi du regard pour montrer où l'utilisateur se concentre.",
    },
    voice: {
      label: "Voice Engine",
      bullets: [
        "Transcription en direct: 'Ouvre README et génère un résumé'",
        "Actions vocales reconnues : 'Recherche', 'Copie', 'Envoie'",
        "Précision adaptative selon le contexte",
      ],
      description: "Simulation de transcription et compréhension vocale en contexte.",
    },
    blackhole: {
      label: "Black Hole",
      bullets: [
        "Scanning : docs/, src/, README.md",
        "34 fichiers indexés, 12 éléments analysés",
        "Extraction de métadonnées et relations de fichiers",
      ],
      description: "Simulation d'analyse de fichiers pour montrer le scan et l'indexation.",
    },
  };

  const startDemo = (agentId, agentName) => {
    setDemoAgent(agentId);
    addToast?.("success", "Démo lancée", `${agentName} est en simulation`, 4800, { confetti: true });
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", animation: "fadeUp .35s ease both" }}>
        <div>
          <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 8 }}>Gestionnaire d'agents</div>
          <h1 style={{ fontSize: 28, fontWeight: 600, color: "#E2E8F0", letterSpacing: "-0.02em" }}>Agents</h1>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 16px", borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.07)" }}>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: activeCount > 0 ? "#10B981" : "#6B7280", ...(activeCount > 0 ? { animation: "pulse 2s ease infinite" } : {}) }} />
          <span style={{ fontSize: 13, color: "rgba(226,232,240,.6)" }}>{activeCount} actif{activeCount !== 1 ? "s" : ""}</span>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {agents.map(({ id, name, desc, Icon, color, stat, score, active }, i) => {
          // Si l'icône passée est une fonction (Lucide component), on l'utilise.
          // Sinon, on cherche dans ICON_MAP, ou fallback sur Bot.
          const RenderIcon = typeof Icon === "function" ? Icon : (ICON_MAP[Icon] || Bot);

          return (
            <div key={id} className="agent-card" style={{ animationDelay: `${i * 0.07}s`, ...(active ? { borderColor: `${color}28`, boxShadow: `0 0 20px ${color}0d` } : {}) }}>
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <div style={{
                    width: 40,
                    height: 40,
                    borderRadius: 12,
                    background: active ? `${color}20` : "rgba(255,255,255,.05)",
                    border: `1px solid ${active ? color + "40" : "rgba(255,255,255,.07)"}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    transition: "all .3s ease"
                  }}>
                    <RenderIcon size={18} color={active ? color : "rgba(226,232,240,.35)"} strokeWidth={1.5} />
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 500, color: "#E2E8F0", marginBottom: 2 }}>{name}</div>
                    <div style={{ fontSize: 11, color: "rgba(226,232,240,.35)" }}>{desc}</div>
                  </div>
                </div>
                <button
                  className={`toggle ${active ? "on" : "off"}`}
                  onClick={() => onToggleAgent(id)}
                  style={active ? { background: color } : {}}
                />
              </div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: 12, borderTop: "1px solid rgba(255,255,255,.05)" }}>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <span style={{ fontSize: 11, color: "rgba(226,232,240,.35)", letterSpacing: "0.08em", textTransform: "uppercase" }}>Score</span>
                  <span style={{ fontSize: 20, fontWeight: 600, fontFamily: "'JetBrains Mono',monospace", color: active ? color : "rgba(226,232,240,.35)" }}>
                    {typeof score === "number" ? score : "—"}
                  </span>
                  <span style={{ fontSize: 11, fontFamily: "'JetBrains Mono',monospace", color: active ? "rgba(226,232,240,.55)" : "rgba(226,232,240,.28)" }}>
                    {stat}
                  </span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8, alignItems: "flex-end" }}>
                  <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, background: active ? `${color}18` : "rgba(255,255,255,.04)", color: active ? color : "rgba(226,232,240,.28)", fontWeight: 500 }}>
                    {active ? "En ligne" : "Hors ligne"}
                  </span>
                  {!active && (id === "eyetrack" || id === "voice" || id === "blackhole") && (
                    <button className="btn sm" onClick={() => startDemo(id, name)}>
                      Voir démo
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {demoAgent && demoConfigs[demoAgent] && (
        <div className="glass" style={{ padding: 24, marginTop: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
            <div style={{ minWidth: 240 }}>
              <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 8 }}>Mode Démo</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: "#E2E8F0" }}>{demoConfigs[demoAgent].label}</div>
              <div style={{ fontSize: 12, color: "rgba(226,232,240,.6)", marginTop: 10, maxWidth: 520 }}>{demoConfigs[demoAgent].description}</div>
            </div>
            <button className="btn danger sm" onClick={() => setDemoAgent(null)} style={{ alignSelf: "flex-start" }}>
              Arrêter la démo
            </button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginTop: 18 }}>
            {demoConfigs[demoAgent].bullets.map((bullet) => (
              <div key={bullet} style={{ padding: 14, borderRadius: 16, background: "rgba(255,255,255,.03)", border: "1px solid rgba(255,255,255,.06)" }}>
                <div style={{ fontSize: 13, color: "#E2E8F0", marginBottom: 8 }}>•</div>
                <div style={{ fontSize: 13, color: "rgba(226,232,240,.7)", lineHeight: 1.6 }}>{bullet}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Agents;
