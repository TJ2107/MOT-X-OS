import { useState, useEffect, useRef } from "react";
import { Send, ChevronRight } from "lucide-react";

const SLabel = ({ children }) => (
  <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 16 }}>
    {children}
  </div>
);

const QUICK_CMDS = [
  { label: "Démarrer Shadow",  cmd: "shadow.start()",          color: "#A78BFA" },
  { label: "Chercher fichier", cmd: "nexus.search('')",         color: "#60A5FA" },
  { label: "État cognitif",    cmd: "cognitive.detect()",       color: "#34D399" },
  { label: "Mémoire épisodique", cmd: "rewind.capture()",       color: "#F59E0B" },
  { label: "Lister agents",    cmd: "agents.list()",            color: "#F472B6" },
  { label: "Statut système",   cmd: "system.status()",          color: "#6B7280" },
];

function Execution({ run, executionLog, onRunCommand }) {
  const [cmd, setCmd] = useState("");
  const logRef = useRef(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [executionLog]);

  const doRun = (command) => {
    const c = command || cmd.trim();
    if (!c) return;
    setCmd("");
    onRunCommand(c);
  };

  const statusColor = { ok: "#10B981", error: "#EF4444", pending: "#F59E0B", warn: "#F97316" };
  const statusIcon  = { ok: "✓", error: "✕", pending: "●", warn: "⚠" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14, height: "100%" }}>
      <div style={{ animation: "fadeUp .35s ease both" }}>
        <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 8 }}>Terminal interactif</div>
        <h1 style={{ fontSize: 28, fontWeight: 600, color: "#E2E8F0", letterSpacing: "-0.02em" }}>Exécution</h1>
      </div>

      <div style={{ display: "flex", gap: 14, flex: 1, minHeight: 0 }}>
        <div className="glass" style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minHeight: 0 }}>
          <div ref={logRef} style={{ flex: 1, overflow: "auto", padding: "22px 26px" }}>
            {executionLog.map(e => {
              const isNexusRecover = e.effect === "nexus_recover" || e.effect === "nexus_recover_denied";
              const lineStatus = e.status || "pending";
              return (
                <div key={e.id} className={`log-line${isNexusRecover ? " nexus-recover-entry" : ""}`}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 10, color: "rgba(226,232,240,.22)", fontFamily: "monospace", flexShrink: 0 }}>{e.time}</span>
                    <span style={{ color: isNexusRecover ? "#F87171" : "#60A5FA", fontFamily: "monospace", fontWeight: 600 }}>$</span>
                    <span style={{ color: "#E2E8F0", fontFamily: "'JetBrains Mono',monospace", fontSize: 13 }}>{e.cmd}</span>
                    <span style={{ color: statusColor[lineStatus] || statusColor.pending, fontSize: 12, marginLeft: 4 }}>{statusIcon[lineStatus] || statusIcon.pending}</span>
                  </div>
                  <div className={isNexusRecover ? "nexus-out" : ""} style={!isNexusRecover ? { color: "rgba(226,232,240,.45)", fontSize: 12, fontFamily: "'JetBrains Mono',monospace", marginLeft: 62, marginTop: 3 } : { marginLeft: 4 }}>
                    {isNexusRecover ? e.out : `→ ${e.out}`}
                  </div>
                </div>
              );
            })}
          </div>
          <div style={{ padding: "14px 22px", borderTop: "1px solid rgba(255,255,255,.06)", display: "flex", alignItems: "center", gap: 10, background: "rgba(255,255,255,.02)" }}>
            <span style={{ color: "#60A5FA", fontFamily: "monospace", fontSize: 16, fontWeight: 700 }}>$</span>
            <input
              className="cmd-input"
              value={cmd}
              onChange={e => setCmd(e.target.value)}
              onKeyDown={e => e.key === "Enter" && doRun()}
              placeholder="nexus.search('mot-clé') · nexus.recover('id') déconseillé…"
            />
            <button className="btn primary sm" onClick={() => doRun()}><Send size={12} strokeWidth={1.5} /></button>
          </div>
        </div>

        <div style={{ width: 220, display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="glass" style={{ padding: 20, flex: 1, overflow: "auto" }}>
            <SLabel>Raccourcis</SLabel>
            <div style={{ fontSize: 10, color: "rgba(252,165,165,.45)", lineHeight: 1.45, marginBottom: 10, padding: "8px 10px", borderRadius: 8, border: "1px solid rgba(239,68,68,.15)", background: "rgba(239,68,68,.06)" }}>
              Récupération : <code style={{ fontSize: 10 }}>nexus.recover('file_id')</code> uniquement au terminal — procédure dissuasive, pas de raccourci.
            </div>
            {QUICK_CMDS.map(({ label, cmd: c }) => (
              <div key={c} className="shortcut-row" onClick={() => doRun(c)}>
                <span style={{ fontSize: 12, color: "rgba(226,232,240,.6)" }}>{label}</span>
                <ChevronRight size={12} color="rgba(226,232,240,.2)" strokeWidth={1.5} />
              </div>
            ))}
          </div>
          <div className="glass" style={{ padding: 20 }}>
            <SLabel>Historique</SLabel>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontSize: 12, color: "rgba(226,232,240,.4)" }}>Total</span>
              <span style={{ fontSize: 13, color: "#E2E8F0", fontFamily: "monospace" }}>{executionLog.length}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ fontSize: 12, color: "rgba(226,232,240,.4)" }}>Succès</span>
              <span style={{ fontSize: 13, color: "#10B981", fontFamily: "monospace" }}>{executionLog.filter(l => l.status === "ok").length}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ fontSize: 12, color: "rgba(226,232,240,.4)" }}>Erreurs</span>
              <span style={{ fontSize: 13, color: "#EF4444", fontFamily: "monospace" }}>{executionLog.filter(l => l.status === "error").length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Execution;
