import { useState, useEffect } from "react";
import { X, CheckCircle, AlertCircle, Info, Zap, Sparkles } from "lucide-react";

function playToastTone(type) {
  if (typeof window === "undefined" || !window.AudioContext) return;
  try {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    const frequencies = {
      success: 880,
      error: 240,
      info: 620,
      shadow: 520,
      progress: 440,
    };
    oscillator.frequency.value = frequencies[type] || 580;
    gain.gain.setValueAtTime(0.001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.03, context.currentTime + 0.02);
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + 0.12);
  } catch {
    // Ignore audio failures in restricted environments
  }
}

function Toast({ id, type = "info", title, message, duration = 4000, progress, confetti, onClose }) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    playToastTone(type);
  }, [type]);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => onClose?.(id), 300);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, id, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => onClose?.(id), 300);
  };

  const typeConfig = {
    success: {
      Icon: CheckCircle,
      color: "#10B981",
      bg: "rgba(16,185,129,0.1)",
      border: "rgba(16,185,129,0.3)",
    },
    error: {
      Icon: AlertCircle,
      color: "#EF4444",
      bg: "rgba(239,68,68,0.1)",
      border: "rgba(239,68,68,0.3)",
    },
    info: {
      Icon: Info,
      color: "#60A5FA",
      bg: "rgba(96,165,250,0.1)",
      border: "rgba(96,165,250,0.3)",
    },
    shadow: {
      Icon: Zap,
      color: "#A78BFA",
      bg: "rgba(167,139,250,0.1)",
      border: "rgba(167,139,250,0.3)",
    },
    progress: {
      Icon: Sparkles,
      color: "#F59E0B",
      bg: "rgba(245,158,11,0.1)",
      border: "rgba(245,158,11,0.3)",
    },
  };

  const config = typeConfig[type] || typeConfig.info;
  const { Icon, color, bg, border } = config;

  const confettiPieces = confetti
    ? Array.from({ length: 10 }).map((_, index) => ({
        id: index,
        left: Math.random() * 100,
        size: 6 + Math.random() * 6,
        color: ["#60A5FA", "#A78BFA", "#FBBF24", "#10B981", "#F472B6"][index % 5],
        delay: `${Math.random() * 200}ms`,
        duration: `${1200 + Math.random() * 400}ms`,
      }))
    : [];

  return (
    <div
      style={{
        position: "relative",
        animation: isVisible
          ? "slideInRight 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)"
          : "slideOutRight 0.3s ease-out",
        padding: "14px 16px",
        borderRadius: 12,
        background: bg,
        border: `1px solid ${border}`,
        display: "flex",
        alignItems: "flex-start",
        gap: 12,
        minWidth: 300,
        maxWidth: 420,
        boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
        overflow: "hidden",
      }}
    >
      {confettiPieces.length > 0 && (
        <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
          {confettiPieces.map((piece) => (
            <span
              key={piece.id}
              style={{
                position: "absolute",
                top: 8,
                left: `${piece.left}%`,
                width: piece.size,
                height: piece.size * 1.4,
                background: piece.color,
                opacity: 0.9,
                transform: "rotate(10deg)",
                borderRadius: 3,
                animation: `confettiFloat ${piece.duration} ease-out ${piece.delay} forwards`,
              }}
            />
          ))}
        </div>
      )}
      <Icon size={18} color={color} strokeWidth={2} style={{ flexShrink: 0, marginTop: 2 }} />
      <div style={{ flex: 1 }}>
        {title && (
          <div style={{ fontSize: 13, fontWeight: 600, color, marginBottom: 4 }}>
            {title}
          </div>
        )}
        {message && (
          <div style={{ fontSize: 12, color: "rgba(226,232,240,0.7)", marginBottom: progress ? 8 : 0 }}>
            {message}
          </div>
        )}
        {progress && (
          <div style={{ marginTop: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 10, marginBottom: 6, fontSize: 10, color: "rgba(226,232,240,0.54)" }}>
              <span>{progress.label || `${progress.current}/${progress.total}`} </span>
              <span>{Math.round((progress.current / Math.max(1, progress.total)) * 100)}%</span>
            </div>
            <div style={{ width: "100%", height: 8, borderRadius: 8, background: "rgba(255,255,255,.08)" }}>
              <div style={{ width: `${(progress.current / Math.max(1, progress.total)) * 100}%`, height: "100%", borderRadius: 8, background: `linear-gradient(90deg, ${color} 0%, ${border.replace('0.3', '0.8')} 100%)` }} />
            </div>
          </div>
        )}
      </div>
      <button
        onClick={handleClose}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "rgba(226,232,240,0.4)",
          padding: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
        onMouseOver={(e) => (e.target.style.color = "rgba(226,232,240,0.6)")}
        onMouseOut={(e) => (e.target.style.color = "rgba(226,232,240,0.4)")}
      >
        <X size={16} strokeWidth={2} />
      </button>

      <style>{`
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(20px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideOutRight {
          from { opacity: 1; transform: translateX(0); }
          to { opacity: 0; transform: translateX(20px); }
        }
        @keyframes confettiFloat {
          to { transform: translateY(100px) rotate(45deg); opacity: 0; }
        }
      `}</style>
    </div>
  );
}

export function ToastContainer({ toasts, onClose }) {
  return (
    <div
      style={{
        position: "fixed",
        bottom: 20,
        right: 20,
        display: "flex",
        flexDirection: "column",
        gap: 10,
        zIndex: 2000,
        pointerEvents: "auto",
      }}
    >
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          title={toast.title}
          message={toast.message}
          duration={toast.duration}
          onClose={onClose}
        />
      ))}
    </div>
  );
}

export default Toast;
