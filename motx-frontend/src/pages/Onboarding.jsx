import { useState, useEffect } from "react";
import { Play, X, ArrowRight } from "lucide-react";

function Onboarding({ onComplete }) {
  const [step, setStep] = useState(0);
  const [appActive, setAppActive] = useState(0);
  const [detected, setDetected] = useState(false);

  const apps = ["VSCode", "Chrome", "Slack", "Terminal"];
  const workflows = [
    "Git Commit Flow",
    "Documentation Update",
    "Code Review"
  ];

  // Animation de simulation Shadow Mode
  useEffect(() => {
    if (step === 1) {
      const interval = setInterval(() => {
        setAppActive((prev) => (prev + 1) % apps.length);
      }, 1500);
      
      const detectTimer = setTimeout(() => setDetected(true), 4500);
      
      return () => {
        clearInterval(interval);
        clearTimeout(detectTimer);
      };
    }
  }, [step]);

  const steps_content = [
    {
      title: "🕵️ Bienvenue dans Shadow Mode",
      subtitle: "L'observateur silencieux de vos routines",
      description: "Shadow Mode observe votre façon de travailler, détecte vos patterns répétitifs et propose automatiquement des workflows pour les automatiser.",
      cta: "Découvrir",
    },
    {
      title: "Comment ça marche en 3 étapes",
      subtitle: "Observation → Détection → Automatisation",
      description: "Regardez Shadow Mode en action",
      demo: true,
    },
    {
      title: "🎯 C'est tout !",
      subtitle: "Prêt à démarrer ?",
      description: "Vous pouvez maintenant explorer Shadow Mode et les autres agents. Commencez par l'onglet Agents pour activer les services.",
      cta: "Commencer",
    },
  ];

  const content = steps_content[step];

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "linear-gradient(135deg, rgba(5,11,24,0.95) 0%, rgba(15,23,42,0.98) 100%)",
        backdropFilter: "blur(10px)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        animation: "fadeIn 0.4s ease-out",
      }}
    >
      {/* Close button */}
      <button
        onClick={onComplete}
        style={{
          position: "absolute",
          top: 20,
          right: 20,
          background: "rgba(255,255,255,0.1)",
          border: "1px solid rgba(255,255,255,0.2)",
          borderRadius: 8,
          width: 40,
          height: 40,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          transition: "all 0.2s ease",
        }}
        onMouseOver={(e) => {
          e.target.style.background = "rgba(255,255,255,0.15)";
        }}
        onMouseOut={(e) => {
          e.target.style.background = "rgba(255,255,255,0.1)";
        }}
      >
        <X size={20} color="rgba(226,232,240,0.6)" strokeWidth={1.5} />
      </button>

      <div
        style={{
          maxWidth: 700,
          width: "90%",
          animation: "slideUp 0.5s ease-out",
        }}
      >
        {/* Header */}
        <div style={{ marginBottom: 40, textAlign: "center" }}>
          <h1
            style={{
              fontSize: 32,
              fontWeight: 700,
              color: "#E2E8F0",
              marginBottom: 8,
              letterSpacing: "-0.02em",
            }}
          >
            {content.title}
          </h1>
          <p
            style={{
              fontSize: 14,
              color: "rgba(226,232,240,0.6)",
              marginBottom: 16,
              letterSpacing: "0.02em",
            }}
          >
            {content.subtitle}
          </p>
        </div>

        {/* Demo Animation */}
        {content.demo ? (
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 16,
              padding: 32,
              marginBottom: 32,
              minHeight: 300,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 20,
            }}
          >
            {/* Step 1: App switching animation */}
            <div style={{ width: "100%", textAlign: "center" }}>
              <div
                style={{
                  fontSize: 11,
                  color: "rgba(226,232,240,0.4)",
                  marginBottom: 12,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                }}
              >
                Étape 1 : Observation
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 8,
                  flexWrap: "wrap",
                }}
              >
                {apps.map((app, i) => (
                  <div
                    key={app}
                    style={{
                      padding: "8px 16px",
                      borderRadius: 8,
                      background:
                        i === appActive
                          ? "rgba(167,139,250,0.3)"
                          : "rgba(255,255,255,0.05)",
                      border: `1px solid ${
                        i === appActive
                          ? "rgba(167,139,250,0.6)"
                          : "rgba(255,255,255,0.1)"
                      }`,
                      color:
                        i === appActive
                          ? "#C4B5FD"
                          : "rgba(226,232,240,0.5)",
                      fontSize: 12,
                      fontWeight: 500,
                      transition: "all 0.3s ease",
                      boxShadow:
                        i === appActive
                          ? "0 0 12px rgba(167,139,250,0.3)"
                          : "none",
                    }}
                  >
                    {app}
                  </div>
                ))}
              </div>
            </div>

            {/* Arrow */}
            <div
              style={{
                animation: "bounce 2s ease-in-out infinite",
              }}
            >
              <ArrowRight size={20} color="rgba(96,165,250,0.5)" strokeWidth={1.5} />
            </div>

            {/* Step 2: Pattern detection */}
            <div style={{ width: "100%", textAlign: "center" }}>
              <div
                style={{
                  fontSize: 11,
                  color: "rgba(226,232,240,0.4)",
                  marginBottom: 12,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                }}
              >
                Étape 2 : Détection de patterns
              </div>
              {detected && (
                <div
                  style={{
                    animation: "slideDown 0.5s ease-out",
                    padding: 12,
                    borderRadius: 8,
                    background: "rgba(16,185,129,0.1)",
                    border: "1px solid rgba(16,185,129,0.4)",
                    color: "#6EE7B7",
                    fontSize: 13,
                  }}
                >
                  ✅ Pattern détecté : Git Commit Flow (confiance 78%)
                </div>
              )}
              {!detected && (
                <div
                  style={{
                    padding: 12,
                    borderRadius: 8,
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    color: "rgba(226,232,240,0.5)",
                    fontSize: 13,
                    animation: "pulse 2s ease-in-out infinite",
                  }}
                >
                  🧠 En train d'analyser...
                </div>
              )}
            </div>

            {/* Arrow */}
            {detected && (
              <div
                style={{
                  animation: "bounce 2s ease-in-out infinite",
                }}
              >
                <ArrowRight size={20} color="rgba(96,165,250,0.5)" strokeWidth={1.5} />
              </div>
            )}

            {/* Step 3: Workflow proposal */}
            {detected && (
              <div style={{ width: "100%", textAlign: "center" }}>
                <div
                  style={{
                    fontSize: 11,
                    color: "rgba(226,232,240,0.4)",
                    marginBottom: 12,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}
                >
                  Étape 3 : Workflows proposés
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {workflows.slice(0, 2).map((workflow) => (
                    <div
                      key={workflow}
                      style={{
                        animation: "slideUp 0.5s ease-out",
                        padding: 10,
                        borderRadius: 8,
                        background: "rgba(96,165,250,0.1)",
                        border: "1px solid rgba(96,165,250,0.3)",
                        color: "#93C5FD",
                        fontSize: 12,
                      }}
                    >
                      🎯 {workflow}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 16,
              padding: 32,
              marginBottom: 32,
              textAlign: "center",
            }}
          >
            <p
              style={{
                color: "rgba(226,232,240,0.7)",
                fontSize: 14,
                lineHeight: 1.6,
              }}
            >
              {content.description}
            </p>
          </div>
        )}

        {/* Navigation */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
          }}
        >
          {step > 0 && (
            <button
              onClick={() => setStep(step - 1)}
              style={{
                padding: "12px 24px",
                borderRadius: 10,
                background: "rgba(255,255,255,0.08)",
                border: "1px solid rgba(255,255,255,0.15)",
                color: "rgba(226,232,240,0.7)",
                fontSize: 13,
                fontWeight: 500,
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
              onMouseOver={(e) => {
                e.target.style.background = "rgba(255,255,255,0.12)";
              }}
              onMouseOut={(e) => {
                e.target.style.background = "rgba(255,255,255,0.08)";
              }}
            >
              Précédent
            </button>
          )}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            {steps_content.map((_, i) => (
              <div
                key={i}
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background:
                    i === step
                      ? "#A78BFA"
                      : i < step
                      ? "#10B981"
                      : "rgba(255,255,255,0.2)",
                  transition: "all 0.3s ease",
                }}
              />
            ))}
          </div>

          <button
            onClick={() => {
              if (step < steps_content.length - 1) {
                setStep(step + 1);
                setDetected(false);
                setAppActive(0);
              } else {
                onComplete();
              }
            }}
            style={{
              padding: "12px 24px",
              borderRadius: 10,
              background: "#A78BFA",
              border: "none",
              color: "#050B18",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 8,
              transition: "all 0.2s ease",
            }}
            onMouseOver={(e) => {
              e.target.style.background = "#C4B5FD";
              e.target.style.transform = "translateY(-2px)";
            }}
            onMouseOut={(e) => {
              e.target.style.background = "#A78BFA";
              e.target.style.transform = "translateY(0)";
            }}
          >
            {step < steps_content.length - 1 ? "Suivant" : "Commencer"}
            <ArrowRight size={14} strokeWidth={2} />
          </button>
        </div>

        {/* Skip link */}
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <button
            onClick={onComplete}
            style={{
              background: "none",
              border: "none",
              color: "rgba(226,232,240,0.4)",
              fontSize: 12,
              cursor: "pointer",
              textDecoration: "underline",
              transition: "color 0.2s ease",
            }}
            onMouseOver={(e) => {
              e.target.style.color = "rgba(226,232,240,0.6)";
            }}
            onMouseOut={(e) => {
              e.target.style.color = "rgba(226,232,240,0.4)";
            }}
          >
            Ignorer cette introduction
          </button>
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(8px); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}

export default Onboarding;
