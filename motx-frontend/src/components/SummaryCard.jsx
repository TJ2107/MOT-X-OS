import React from "react";

function SummaryCard({ metrics = {} }) {
  const learned = metrics.learnedWorkflows || 0;
  const recent = metrics.lastDetected ? new Date(metrics.lastDetected).toLocaleString("fr-FR") : "—";
  const topPatterns = metrics.topPatterns || [];

  return (
    <div className="glass" style={{ padding: 18, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
        <div style={{ width: 64, height: 64, borderRadius: 12, background: "linear-gradient(135deg,#A78BFA,#60A5FA)", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 700, fontSize: 20 }}>
          {learned}
        </div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#E2E8F0" }}>Shadow Mode — Résumé</div>
          <div style={{ fontSize: 12, color: "rgba(226,232,240,.6)", marginTop: 6 }}>Dernière détection : {recent}</div>
          <div style={{ fontSize: 12, color: "rgba(226,232,240,.5)", marginTop: 8 }}>
            Top patterns: {topPatterns.length ? topPatterns.slice(0,3).join(', ') : 'Aucun encore'}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
        <div style={{ fontSize: 12, color: "rgba(226,232,240,.5)" }}>Progression apprentissage</div>
        <div style={{ width: 220, height: 10, background: "rgba(255,255,255,.04)", borderRadius: 10, overflow: "hidden" }}>
          <div style={{ width: `${Math.round((metrics.learningProgress || 0) * 100)}%`, height: "100%", background: "linear-gradient(90deg,#F59E0B,#10B981)" }} />
        </div>
        <div style={{ fontSize: 12, color: "rgba(226,232,240,.36)" }}>{Math.round((metrics.learningProgress || 0) * 100)}% complet</div>
      </div>
    </div>
  );
}

export default SummaryCard;
