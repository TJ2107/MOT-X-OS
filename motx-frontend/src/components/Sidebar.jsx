import { Wifi, WifiOff, Database } from "lucide-react";

function Sidebar({ active, setActive, connected, services, navItems }) {
  const chromaStatus = services.find((s) => s.label === 'ChromaDB')?.status ?? 'Hors ligne';
  const chromaColor = chromaStatus === 'En ligne' ? 'rgba(16,185,129,.85)' : 'rgba(239,68,68,.75)';

  return (
    <aside style={{
      width: 216,
      height: "100vh",
      flexShrink: 0,
      display: "flex",
      flexDirection: "column",
      padding: "28px 14px",
      background: "rgba(5, 11, 24, 0.75)",
      borderRight: "1px solid rgba(255, 255, 255, 0.06)",
      backdropFilter: "blur(40px)",
      boxShadow: "4px 0 48px rgba(0,0,0,0.55)",
      position: "relative",
      zIndex: 20
    }}>
      <div style={{ paddingLeft: 6, marginBottom: 36 }}>
        <div style={{ fontSize: 19, fontWeight: 600, letterSpacing: "0.04em", color: "#E2E8F0" }}>MOT-X</div>
        <div style={{ fontSize: 10, color: "rgba(226, 232, 240, 0.25)", letterSpacing: "0.18em", textTransform: "uppercase", marginTop: 4 }}>Cognitive OS · v2</div>
      </div>
      
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "8px 12px",
        borderRadius: 10,
        marginBottom: 28,
        background: connected ? "rgba(16, 185, 129, 0.12)" : "rgba(239, 68, 68, 0.07)",
        border: `1px solid ${connected ? "rgba(16, 185, 129, 0.2)" : "rgba(239, 68, 68, 0.14)"}`
      }}>
        {connected ? (
          <Wifi size={12} color="rgba(110, 231, 183, 0.85)" strokeWidth={1.5} />
        ) : (
          <WifiOff size={12} color="rgba(252, 165, 165, 0.6)" strokeWidth={1.5} />
        )}
        <span style={{
          fontSize: 12,
          color: connected ? "rgba(110, 231, 183, 0.9)" : "rgba(252, 165, 165, 0.7)",
          fontWeight: 500
        }}>
          {connected ? "Connecté" : "Déconnecté"}
        </span>
        <div style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: connected ? "#10B981" : "#EF4444",
          marginLeft: "auto",
          animation: "pulse 2s ease infinite"
        }} />
      </div>

      <nav style={{ display: "flex", flexDirection: "column", gap: 3, flex: 1 }}>
        {navItems.map(({ id, label, Icon }) => (
          <div
            key={id}
            className={`nav-item${active === id ? " active" : ""}`}
            onClick={() => setActive(id)}
          >
            <Icon size={15} strokeWidth={1.5} />
            {label}
          </div>
        ))}
      </nav>

      <div style={{
        padding: "12px 14px",
        borderRadius: 12,
        background: "rgba(255, 255, 255, 0.025)",
        border: "1px solid rgba(255, 255, 255, 0.05)"
      }}>
        <div style={{
          fontSize: 10,
          color: "rgba(226, 232, 240, 0.22)",
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          marginBottom: 6
        }}>
          Système
        </div>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          fontSize: 12,
          color: chromaColor
        }}>
          <Database size={11} strokeWidth={1.5} />
          ChromaDB · {chromaStatus}
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
