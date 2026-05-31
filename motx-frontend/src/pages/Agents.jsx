import { Database, Eye, Mic, Scan, RotateCcw, Bot } from "lucide-react";

// Dictionnaire pour mapper les chaînes d'icônes à des composants Lucide réels
const ICON_MAP = {
  Database: Database,
  Eye: Eye,
  Mic: Mic,
  Scan: Scan,
  RotateCcw: RotateCcw,
};

function Agents({ agents, onToggleAgent }) {
  const activeCount = agents.filter(a => a.active).length;

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
                <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, background: active ? `${color}18` : "rgba(255,255,255,.04)", color: active ? color : "rgba(226,232,240,.28)", fontWeight: 500 }}>
                  {active ? "En ligne" : "Hors ligne"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Agents;
