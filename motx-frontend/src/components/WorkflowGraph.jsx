import { Zap, Eye, Mic, Database } from "lucide-react";

function WorkflowGraph({ workflows = [] }) {
  if (!workflows || workflows.length === 0) {
    return (
      <div className="glass" style={{ padding: 24, minHeight: 180, display: "flex", alignItems: "center", justifyContent: "center", color: "rgba(226,232,240,.4)" }}>
        Aucun workflow disponible pour la visualisation.
      </div>
    );
  }

  const sampleWorkflows = workflows.slice(0, 2);

  const createSteps = (workflow) => {
    const appName = workflow.source || "VS Code";
    return [
      { label: appName, icon: Eye, accent: "#60A5FA" },
      { label: workflow.name, icon: Zap, accent: "#A78BFA" },
      { label: "Action proposée", icon: Database, accent: "#10B981" },
    ];
  };

  return (
    <div className="glass" style={{ padding: 24 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
        <div>
          <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 8 }}>Visualisation workflows</div>
          <div style={{ fontSize: 18, fontWeight: 600, color: "#E2E8F0" }}>Flux → action</div>
        </div>
        <div style={{ fontSize: 11, color: "rgba(226,232,240,.5)", padding: "8px 12px", borderRadius: 12, background: "rgba(255,255,255,.05)" }}>
          {workflows.length} workflow{s(workflows.length)} analysé{s(workflows.length)}
        </div>
      </div>

      <div style={{ display: "grid", gap: 18 }}>
        {sampleWorkflows.map((workflow, index) => {
          const steps = createSteps(workflow);
          return (
            <div key={workflow.id || index} style={{ display: "grid", gap: 12, padding: 16, borderRadius: 18, background: "rgba(255,255,255,.02)", border: "1px solid rgba(255,255,255,.08)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                <div>
                  <div style={{ fontSize: 13, color: "rgba(226,232,240,.5)", marginBottom: 4 }}>Workflow</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: "#E2E8F0" }}>{workflow.name}</div>
                </div>
                <div style={{ fontSize: 12, padding: "4px 10px", borderRadius: 999, background: workflow.confidence >= 0.75 ? "rgba(16,185,129,.12)" : "rgba(245,158,11,.12)", color: workflow.confidence >= 0.75 ? "#6EE7B7" : "#F59E0B" }}>
                  Confiance {workflow.confidence ? `${Math.round(workflow.confidence * 100)}%` : "—"}
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
                {steps.map((step, stepIndex) => {
                  const Icon = step.icon;
                  return (
                    <div key={step.label} style={{ display: "flex", alignItems: "center", gap: 10, background: "rgba(255,255,255,.05)", border: `1px solid ${step.accent}22`, borderRadius: 16, padding: "12px 14px", minWidth: 140, flex: 1, position: "relative" }}>
                      <div style={{ width: 34, height: 34, borderRadius: 12, background: step.accent, display: "flex", alignItems: "center", justifyContent: "center", color: "white" }}>
                        <Icon size={18} strokeWidth={2} />
                      </div>
                      <div>
                        <div style={{ fontSize: 12, color: "rgba(226,232,240,.5)", marginBottom: 4 }}>Étape {stepIndex + 1}</div>
                        <div style={{ fontSize: 14, fontWeight: 600, color: "#E2E8F0" }}>{step.label}</div>
                      </div>
                      {stepIndex < steps.length - 1 && (
                        <div style={{ position: "absolute", right: -13, top: "50%", transform: "translateY(-50%)" }}>
                          <div style={{ width: 24, height: 2, background: "rgba(226,232,240,.18)" }} />
                          <div style={{ width: 0, height: 0, borderLeft: "7px solid rgba(226,232,240,.18)", borderTop: "5px solid transparent", borderBottom: "5px solid transparent", position: "absolute", right: -7, top: -4 }} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              {workflow.description && <div style={{ fontSize: 12, color: "rgba(226,232,240,.55)", marginTop: 6 }}>{workflow.description}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function s(count) {
  return count > 1 ? "s" : "";
}

export default WorkflowGraph;
