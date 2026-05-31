import { Zap, TrendingUp } from "lucide-react";

function WorkflowTimeline({ workflows = [], onAccept, onReject }) {
  if (!workflows || workflows.length === 0) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: 200,
          gap: 8,
        }}
      >
        <TrendingUp size={24} color="rgba(226,232,240,.12)" strokeWidth={1.2} />
        <span style={{ fontSize: 12, color: "rgba(226,232,240,.22)" }}>
          Aucun workflow découvert pour le moment
        </span>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {workflows.map((workflow, index) => (
        <div
          key={workflow.id || index}
          style={{
            display: "flex",
            gap: 12,
            animation: `slideIn 0.4s ease-out`,
            animationDelay: `${index * 0.05}s`,
            animationFillMode: "both",
          }}
        >
          {/* Timeline connector */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 8,
              paddingRight: 12,
              position: "relative",
            }}
          >
            {/* Dot */}
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: "#A78BFA",
                boxShadow: "0 0 8px rgba(167,139,250,0.5)",
                animation: "pulse 2s ease-in-out infinite",
              }}
            />
            {/* Line to next */}
            {index < workflows.length - 1 && (
              <div
                style={{
                  flex: 1,
                  width: 2,
                  background: "linear-gradient(180deg, rgba(167,139,250,0.5) 0%, rgba(167,139,250,0.1) 100%)",
                  minHeight: 60,
                }}
              />
            )}
          </div>

          {/* Content */}
          <div style={{ flex: 1, paddingTop: 2 }}>
            <div
              style={{
                padding: "12px 14px",
                borderRadius: 12,
                background: "rgba(255,255,255,.02)",
                border: "1px solid rgba(167,139,250,.2)",
                transition: "all 0.2s ease",
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,.04)";
                e.currentTarget.style.borderColor = "rgba(167,139,250,.4)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = "rgba(255,255,255,.02)";
                e.currentTarget.style.borderColor = "rgba(167,139,250,.2)";
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                <Zap size={14} color="#A78BFA" strokeWidth={2} />
                <span style={{ fontSize: 12, fontWeight: 600, color: "#E2E8F0" }}>
                  {workflow.name}
                </span>
                {workflow.confidence && (
                  <span
                    style={{
                      fontSize: 10,
                      padding: "2px 8px",
                      borderRadius: 4,
                      background:
                        workflow.confidence > 0.85
                          ? "rgba(16,185,129,0.15)"
                          : workflow.confidence > 0.7
                          ? "rgba(245,158,11,0.15)"
                          : "rgba(96,165,250,0.15)",
                      color:
                        workflow.confidence > 0.85
                          ? "#6EE7B7"
                          : workflow.confidence > 0.7
                          ? "#FBBF24"
                          : "#93C5FD",
                    }}
                  >
                    {(workflow.confidence * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              {workflow.description && (
                <div style={{ fontSize: 11, color: "rgba(226,232,240,.6)" }}>
                  {workflow.description}
                </div>
              )}
              {workflow.timestamp && (
                <div style={{ fontSize: 10, color: "rgba(226,232,240,.4)", marginTop: 6 }}>
                  {new Date(workflow.timestamp).toLocaleTimeString("fr-FR")}
                </div>
              )}

              {/* Action buttons */}
              <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                <button
                  onClick={() => onAccept && onAccept(workflow)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: 8,
                    background: "#10B981",
                    color: "#050B18",
                    fontSize: 12,
                    fontWeight: 600,
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  Accepter
                </button>
                <button
                  onClick={() => onReject && onReject(workflow)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: 8,
                    background: "transparent",
                    color: "rgba(226,232,240,0.8)",
                    fontSize: 12,
                    fontWeight: 600,
                    border: "1px solid rgba(226,232,240,0.06)",
                    cursor: "pointer",
                  }}
                >
                  Rejeter
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}

      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulse {
          0%, 100% { box-shadow: 0 0 8px rgba(167,139,250,0.5); }
          50% { box-shadow: 0 0 16px rgba(167,139,250,0.8); }
        }
      `}</style>
    </div>
  );
}

export default WorkflowTimeline;
