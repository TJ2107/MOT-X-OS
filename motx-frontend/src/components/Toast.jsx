import { useState, useEffect } from "react";
import { X, CheckCircle, AlertCircle, Info, Zap } from "lucide-react";

function Toast({ id, type = "info", title, message, duration = 4000, onClose }) {
  const [isVisible, setIsVisible] = useState(true);

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
  };

  const config = typeConfig[type] || typeConfig.info;
  const { Icon, color, bg, border } = config;

  return (
    <div
      style={{
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
        maxWidth: 400,
        boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
      }}
    >
      <Icon size={18} color={color} strokeWidth={2} style={{ flexShrink: 0, marginTop: 2 }} />
      <div style={{ flex: 1 }}>
        {title && (
          <div style={{ fontSize: 13, fontWeight: 600, color, marginBottom: 4 }}>
            {title}
          </div>
        )}
        {message && (
          <div style={{ fontSize: 12, color: "rgba(226,232,240,0.7)" }}>
            {message}
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
