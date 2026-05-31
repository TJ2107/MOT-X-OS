import React from "react";

function GettingStartedCard({ onStartDemo }) {
  return (
    <div className="glass" style={{ padding: 20, display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
      <div style={{ flex: 1, minWidth: 280 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: "#E2E8F0", marginBottom: 8 }}>Getting Started</div>
        <div style={{ fontSize: 12, color: "rgba(226,232,240,.65)", marginBottom: 16, maxWidth: 560 }}>
          Découvrez Shadow Mode rapidement avec un guide pas à pas. Activez les agents, observez les détections et laissez vos premiers workflows être proposés automatiquement.
        </div>
        <div style={{ display: "grid", gap: 10 }}>
          {[
            "1. Activez Shadow Mode et laissez-le observer en arrière-plan.",
            "2. Regardez les patterns se former dans la timeline.",
            "3. Acceptez ou rejetez les workflows proposés.",
            "4. Utilisez la démo pour simuler une session Shadow en direct.",
          ].map((step) => (
            <div key={step} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <span style={{ width: 20, height: 20, borderRadius: 8, background: "rgba(59,130,246,.15)", color: "#93c5fd", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, marginTop: 2 }}>
                ✓
              </span>
              <p style={{ fontSize: 12, color: "rgba(226,232,240,.72)", lineHeight: 1.6, margin: 0 }}>{step}</p>
            </div>
          ))}
        </div>
      </div>

      <div style={{ minWidth: 240, display: "flex", flexDirection: "column", gap: 14, padding: 18, borderRadius: 20, background: "rgba(255,255,255,.02)", border: "1px solid rgba(255,255,255,.08)" }}>
        <div style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.12em", color: "rgba(226,232,240,.36)" }}>Prêt ?</div>
        <div style={{ fontSize: 20, fontWeight: 700, color: "#E2E8F0" }}>Testez Shadow Mode</div>
        <div style={{ fontSize: 12, color: "rgba(226,232,240,.6)", lineHeight: 1.6 }}>
          Lancez une session de démonstration instantanée pour voir comment MotX détecte les changements d'app, apprend des patterns et propose des workflows.
        </div>
        <button className="btn primary" style={{ alignSelf: "flex-start" }} onClick={onStartDemo}>
          Lancer la démo
        </button>
      </div>
    </div>
  );
}

export default GettingStartedCard;
