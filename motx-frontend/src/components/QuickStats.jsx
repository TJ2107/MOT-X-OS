import { useEffect, useState } from "react";
import { Monitor, Zap, Activity } from "lucide-react";

function CountUp({ value, duration = 700 }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const steps = Math.max(6, Math.round(duration / 50));
    const step = (value - start) / steps;
    const iv = setInterval(() => {
      start += step;
      if ((step > 0 && start >= value) || (step < 0 && start <= value)) {
        setDisplay(value);
        clearInterval(iv);
      } else {
        setDisplay(Math.round(start));
      }
    }, 50);
    return () => clearInterval(iv);
  }, [value, duration]);
  return <span style={{ fontFamily: "'JetBrains Mono',monospace" }}>{display}</span>;
}

function QuickStats({ metrics = {} }) {
  const apps = metrics.detectedApps || 0;
  const patterns = metrics.patternsInProgress || 0;
  const avgConfidence = Math.round((metrics.averageConfidence || 0) * 100);

  const items = [
    { label: "Applications détectées", value: apps, Icon: Monitor, color: "#60A5FA" },
    { label: "Patterns en cours", value: patterns, Icon: Activity, color: "#F59E0B" },
    { label: "Confiance moyenne", value: `${avgConfidence}%`, Icon: Zap, color: "#10B981" },
  ];

  return (
    <div className="glass" style={{ padding: 18, display: "flex", gap: 12, alignItems: "center" }}>
      {items.map((it) => (
        <div key={it.label} style={{ display: "flex", alignItems: "center", gap: 12, minWidth: 160 }}>
          <div style={{ width: 44, height: 44, borderRadius: 10, background: "rgba(255,255,255,.02)", display: "flex", alignItems: "center", justifyContent: "center", border: `1px solid ${it.color}22` }}>
            <it.Icon size={18} color={it.color} strokeWidth={1.5} />
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: "#E2E8F0" }}>
              {typeof it.value === "number" ? <CountUp value={it.value} /> : it.value}
            </div>
            <div style={{ fontSize: 11, color: "rgba(226,232,240,.5)" }}>{it.label}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default QuickStats;
