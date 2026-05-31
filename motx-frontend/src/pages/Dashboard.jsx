import { Zap, CheckCircle, Clock, Bot, Play, BarChart2, Mic, Layers } from "lucide-react";
import WorkflowTimeline from "../components/WorkflowTimeline";
import WorkflowGraph from "../components/WorkflowGraph";
import QuickStats from "../components/QuickStats";
import SummaryCard from "../components/SummaryCard";
import GettingStartedCard from "../components/GettingStartedCard";

const SLabel = ({ children }) => (
  <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 16 }}>
    {children}
  </div>
);

function Dashboard({ ambientUpdate, eyeGaze, run, executionLog, services, dashboardMetrics, agents, onAcceptWorkflow, onRejectWorkflow, addToast }) {
  const recentExecutions = executionLog.slice(0, 5);
  
  // Récupérer les workflows du Shadow Mode agent
  const shadowAgent = agents?.find((a) => a.id === "shadow");
  const workflows = dashboardMetrics?.discoveredWorkflows || [];
  
  const stats = [
    {
      label: "Exécutions",
      sub: "Total",
      value: dashboardMetrics.totalExecutions ?? executionLog.length,
      Icon: Zap,
      color: "#F59E0B",
      glow: "rgba(245,158,11,.14)",
      delay: "0.08s"
    },
    {
      label: "Taux Succès",
      sub: "Réussite",
      value: `${dashboardMetrics.successRate?.toFixed(1) ?? 0}%`,
      Icon: CheckCircle,
      color: "#10B981",
      glow: "rgba(16,185,129,.13)",
      delay: "0.16s"
    },
    {
      label: "Latence moy.",
      sub: "Vitesse",
      value: `${dashboardMetrics.averageSpeed?.toFixed(2) ?? 0}s`,
      Icon: Clock,
      color: "#60A5FA",
      glow: "rgba(96,165,250,.13)",
      delay: "0.24s"
    },
    {
      label: "Agents Actifs",
      sub: "En ligne",
      value: dashboardMetrics.activeAgents ?? services.filter((s) => s.status === "En ligne" || s.status === "Actif").length,
      Icon: Bot,
      color: "#A78BFA",
      glow: "rgba(167,139,250,.13)",
      delay: "0.32s"
    }
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ animation: "fadeUp .35s ease both" }}>
        <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 8 }}>Vue d'ensemble</div>
        <h1 style={{ fontSize: 28, fontWeight: 600, color: "#E2E8F0", letterSpacing: "-0.02em" }}>Dashboard</h1>
      </div>

      <SummaryCard metrics={{ learnedWorkflows: (dashboardMetrics.acceptedWorkflows || []).length, lastDetected: dashboardMetrics.lastDetected, topPatterns: dashboardMetrics.topPatterns, learningProgress: dashboardMetrics.learningProgress || 0 }} />
      <GettingStartedCard onStartDemo={() => addToast && addToast("shadow", "🎮 Démo Shadow Mode lancée", "Simulation de 30s démarrée", 5000, { confetti: true })} />
      <QuickStats metrics={{ detectedApps: dashboardMetrics.detectedApps, patternsInProgress: dashboardMetrics.patternsInProgress, averageConfidence: dashboardMetrics.averageConfidence }} />
      <WorkflowGraph workflows={dashboardMetrics.discoveredWorkflows} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
        {stats.map(({ label, sub, value, Icon, color, glow, delay }) => (
          <div key={label} className="stat-card" style={{ animationDelay: delay }}>
            <div style={{ display: "flex", alignItems: "center", justifycontent: "space-between", justifyContent: "space-between", marginBottom: 16 }}>
              <div style={{ width: 34, height: 34, borderRadius: 10, background: glow, border: `1px solid ${color}28`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon size={14} color={color} strokeWidth={1.5} />
              </div>
              <span style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.12em", textTransform: "uppercase" }}>{sub}</span>
            </div>
            <div style={{ fontSize: 28, fontWeight: 600, color: "#E2E8F0", letterSpacing: "-0.02em", marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>{value}</div>
            <div style={{ fontSize: 13, color: "rgba(226,232,240,.38)" }}>{label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 12 }}>
        <div className="glass" style={{ padding: 24 }}>
          <SLabel>Actions rapides</SLabel>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {[
              { label: "Lancer exécution", Icon: Play, cls: "primary", action: "execution" },
              { label: "Analytiques", Icon: BarChart2, action: "analytiques" },
              { label: "Vérifier agents", Icon: Bot, action: "agents" },
              { label: "Commande vocale", Icon: Mic, action: "cognitif" },
            ].map(({ label, Icon, cls = "", action }) => (
              <button key={label} className={`btn ${cls}`} data-action={action} onClick={() => run && run(action)}>
                <Icon size={12} strokeWidth={1.5} />{label}
              </button>
            ))}
          </div>
        </div>

        <div className="glass" style={{ padding: 24 }}>
          <SLabel>État du système</SLabel>
          <div style={{ display: "grid", gap: 10 }}>
            {services.map((service) => (
              <div key={service.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, padding: "12px 14px", borderRadius: 14, background: "rgba(255,255,255,.02)", border: `1px solid rgba(255,255,255,.06)` }}>
                <span style={{ fontSize: 12, color: "rgba(226,232,240,.7)" }}>{service.label}</span>
                <span style={{ fontSize: 12, color: service.color, fontWeight: 600 }}>{service.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="glass" style={{ padding: 24 }}>
        <SLabel>Workflows Découverts</SLabel>
        <WorkflowTimeline workflows={workflows} onAccept={onAcceptWorkflow} onReject={onRejectWorkflow} />
        <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button className="btn" onClick={() => addToast && addToast('shadow', '🕵️ App change détecté', 'VS Code détecté', 5000, { confetti: false })}>Simuler notification</button>
          <button className="btn" onClick={() => addToast && addToast('progress', '🧠 Pattern en cour de détection', '2/3 occurrences', 5200, { progress: { current: 2, total: 3, label: 'Détection' } })}>Simuler progression</button>
          <button className="btn" onClick={() => addToast && addToast('shadow', '✅ Workflow proposé', 'Git Commit Flow (76%)', 5600, { confetti: true })}>Simuler workflow</button>
        </div>
      </div>

      <div className="glass" style={{ padding: 24 }}>
        <SLabel>Acceptés / Rejetés</SLabel>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <div style={{ fontSize: 12, color: 'rgba(226,232,240,.6)', marginBottom: 8 }}>Acceptés</div>
            {(dashboardMetrics.acceptedWorkflows || []).length === 0 ? (
              <div style={{ fontSize: 12, color: 'rgba(226,232,240,.22)' }}>Aucun</div>
            ) : (
              (dashboardMetrics.acceptedWorkflows || []).map((w) => (
                <div key={w.id} style={{ padding: 8, borderRadius: 8, background: 'rgba(16,185,129,0.06)', marginBottom: 8 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#E2E8F0' }}>{w.name}</div>
                  <div style={{ fontSize: 11, color: 'rgba(226,232,240,.5)' }}>{w.description}</div>
                </div>
              ))
            )}
          </div>

          <div>
            <div style={{ fontSize: 12, color: 'rgba(226,232,240,.6)', marginBottom: 8 }}>Rejetés</div>
            {(dashboardMetrics.rejectedWorkflows || []).length === 0 ? (
              <div style={{ fontSize: 12, color: 'rgba(226,232,240,.22)' }}>Aucun</div>
            ) : (
              (dashboardMetrics.rejectedWorkflows || []).map((w) => (
                <div key={w.id} style={{ padding: 8, borderRadius: 8, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)', marginBottom: 8 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#E2E8F0' }}>{w.name}</div>
                  <div style={{ fontSize: 11, color: 'rgba(226,232,240,.5)' }}>{w.description}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="glass" style={{ padding: 24 }}>
        <SLabel>Exécutions récentes</SLabel>
        {recentExecutions.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {recentExecutions.map((entry) => (
              <div key={entry.id} style={{ padding: "12px 14px", borderRadius: 14, background: "rgba(255,255,255,.02)", border: "1px solid rgba(255,255,255,.06)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 12, color: "rgba(226,232,240,.6)" }}>{entry.time}</span>
                  <span style={{ fontSize: 12, color: entry.status === "ok" ? "#10B981" : entry.status === "pending" ? "#F59E0B" : "#EF4444" }}>
                    {entry.status === "ok" ? "Succès" : entry.status === "pending" ? "En attente" : "Erreur"}
                  </span>
                </div>
                <div style={{ marginTop: 8, color: "rgba(226,232,240,.85)", fontSize: 13, fontFamily: "'JetBrains Mono',monospace" }}>{entry.cmd}</div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 92, gap: 8 }}>
            <Layers size={20} color="rgba(226,232,240,.12)" strokeWidth={1.2} />
            <span style={{ fontSize: 12, color: "rgba(226,232,240,.22)" }}>Aucune exécution enregistrée</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
