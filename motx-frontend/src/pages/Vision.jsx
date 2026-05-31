import { useState, useEffect, useRef } from "react";
import { Crosshair, CheckCircle, AlertTriangle, Scan, Camera, Film } from "lucide-react";

const SLabel = ({ children }) => (
  <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 16 }}>
    {children}
  </div>
);

function Vision() {
  const [gaze, setGaze]         = useState({ x: 50, y: 32 });
  const [tracking, setTracking] = useState(false);
  const [shadow, setShadow]     = useState(false);
  const [calibrated, setCalib]  = useState(false);
  const [calibrating, setCalibing] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (tracking) {
      intervalRef.current = setInterval(() => {
        setGaze({ x: 15 + Math.random() * 70, y: 12 + Math.random() * 48 });
      }, 1300);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [tracking]);

  const calibrate = () => {
    setCalibing(true);
    const pts = [[20, 20], [50, 20], [80, 20], [20, 50], [50, 50], [80, 50], [20, 80], [50, 80], [80, 80]];
    let i = 0;
    const t = setInterval(() => {
      const p = pts[i % pts.length];
      setGaze({ x: 5 + p[0] * 0.9, y: 5 + p[1] * 0.55 });
      i++;
      if (i >= pts.length) {
        clearInterval(t);
        setCalibing(false);
        setCalib(true);
        setTracking(true);
      }
    }, 500);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ animation: "fadeUp .35s ease both" }}>
        <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 8 }}>Eye Tracking · Shadow Mode</div>
        <h1 style={{ fontSize: 28, fontWeight: 600, color: "#E2E8F0", letterSpacing: "-0.02em" }}>Vision</h1>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 14 }}>
        <div className="glass" style={{ padding: 24 }}>
          <SLabel>Suivi oculaire — aperçu écran</SLabel>
          <div style={{ borderRadius: 14, overflow: "hidden", background: "#020509", border: "1px solid rgba(255,255,255,.06)", position: "relative" }}>
            <svg viewBox="0 0 100 62" style={{ width: "100%", display: "block" }}>
              <defs>
                <radialGradient id="gazeGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#60A5FA" stopOpacity="0" />
                </radialGradient>
              </defs>
              {[25, 50, 75].map(x => <line key={x} x1={x} y1="0" x2={x} y2="62" stroke="rgba(255,255,255,.03)" strokeWidth="0.3" />)}
              {[20, 40, 55].map(y => <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="rgba(255,255,255,.03)" strokeWidth="0.3" />)}
              {tracking && <>
                <line x1={gaze.x} y1="0" x2={gaze.x} y2="62" stroke="rgba(96,165,250,.12)" strokeWidth="0.4" />
                <line x1="0" y1={gaze.y} x2="100" y2={gaze.y} stroke="rgba(96,165,250,.12)" strokeWidth="0.4" />
              </>}
              <g className="gaze-group" style={{ transform: `translate(${gaze.x}px, ${gaze.y}px)` }}>
                {tracking ? <>
                  <circle r="12" fill="url(#gazeGlow)" opacity="0.4" />
                  <circle r="6" fill="none" stroke="rgba(96,165,250,.3)" strokeWidth="0.5" />
                  <circle r="2.8" fill={calibrated ? "#60A5FA" : "#F59E0B"} style={{ filter: `drop-shadow(0 0 4px ${calibrated ? "#60A5FA" : "#F59E0B"})` }} />
                  <line x1="-5" y1="0" x2="-2.5" y2="0" stroke="rgba(96,165,250,.8)" strokeWidth="0.5" />
                  <line x1="2.5" y1="0" x2="5" y2="0" stroke="rgba(96,165,250,.8)" strokeWidth="0.5" />
                  <line x1="0" y1="-5" x2="0" y2="-2.5" stroke="rgba(96,165,250,.8)" strokeWidth="0.5" />
                  <line x1="0" y1="2.5" x2="0" y2="5" stroke="rgba(96,165,250,.8)" strokeWidth="0.5" />
                </> : <circle r="2" fill="rgba(226,232,240,.1)" />}
              </g>
            </svg>
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 14 }}>
            <div style={{ display: "flex", gap: 14 }}>
              {[{ l: "X", v: tracking ? `${Math.round(gaze.x)}%` : "—" }, { l: "Y", v: tracking ? `${Math.round(gaze.y)}%` : "—" }].map(({ l, v }) => (
                <div key={l} style={{ fontSize: 12, color: "rgba(226,232,240,.4)", fontFamily: "monospace" }}>
                  <span>{l}: </span>
                  <span style={{ color: tracking ? "#60A5FA" : "rgba(226,232,240,.2)" }}>{v}</span>
                </div>
              ))}
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: tracking ? "#10B981" : "#6B7280", ...(tracking ? { animation: "pulse 2s ease infinite" } : {}) }} />
              <span style={{ fontSize: 11, color: tracking ? "#10B981" : "rgba(226,232,240,.3)" }}>{tracking ? "Actif" : "Inactif"}</span>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="glass" style={{ padding: 22, flex: 1 }}>
            <SLabel>Eye Tracking</SLabel>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", borderRadius: 11, background: "rgba(255,255,255,.03)", border: "1px solid rgba(255,255,255,.06)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Crosshair size={13} color="rgba(226,232,240,.4)" strokeWidth={1.5} />
                  <span style={{ fontSize: 13, color: "rgba(226,232,240,.55)" }}>Tracking</span>
                </div>
                <button
                  className={`toggle ${tracking ? "on" : "off"}`}
                  onClick={() => setTracking(t => !t)}
                  style={tracking ? { background: "#60A5FA" } : {}}
                />
              </div>

              <div style={{
                padding: "10px 14px", borderRadius: 11,
                background: calibrated ? "rgba(16,185,129,.08)" : "rgba(245,158,11,.07)",
                border: `1px solid ${calibrated ? "rgba(16,185,129,.2)" : "rgba(245,158,11,.2)"}`
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
                  {calibrated
                    ? <CheckCircle size={12} color="#10B981" strokeWidth={1.5} />
                    : <AlertTriangle size={12} color="#F59E0B" strokeWidth={1.5} />
                  }
                  <span style={{ fontSize: 12, color: calibrated ? "#10B981" : "#F59E0B", fontWeight: 500 }}>
                    {calibrating ? "Calibration en cours…" : calibrated ? "Calibré (9 pts)" : "Non calibré"}
                  </span>
                </div>
                <button
                  className="btn sm"
                  onClick={calibrate}
                  disabled={calibrating}
                  style={{ width: "100%", justifyContent: "center", opacity: calibrating ? 0.5 : 1 }}
                >
                  <Scan size={11} strokeWidth={1.5} /> {calibrating ? "…" : "Lancer calibration"}
                </button>
              </div>
            </div>
          </div>

          <div className="glass" style={{ padding: 22, flex: 1 }}>
            <SLabel>Shadow Mode</SLabel>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", borderRadius: 11, background: "rgba(255,255,255,.03)", border: "1px solid rgba(255,255,255,.06)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Camera size={13} color="rgba(226,232,240,.4)" strokeWidth={1.5} />
                  <span style={{ fontSize: 13, color: "rgba(226,232,240,.55)" }}>Observation</span>
                </div>
                <button
                  className={`toggle ${shadow ? "on" : "off"}`}
                  onClick={() => setShadow(s => !s)}
                  style={shadow ? { background: "#A78BFA" } : {}}
                />
              </div>
              <div style={{ padding: "10px 14px", borderRadius: 11, background: "rgba(255,255,255,.03)", border: "1px solid rgba(255,255,255,.06)" }}>
                <div style={{ fontSize: 11, color: "rgba(226,232,240,.3)", marginBottom: 6 }}>Intervalle capture</div>
                <div style={{ display: "flex", gap: 6 }}>
                  {["2s", "5s", "10s"].map(v => (
                    <button key={v} className="btn sm" style={{ flex: 1, justifyContent: "center", ...(v === "2s" ? { background: "rgba(167,139,250,.15)", borderColor: "rgba(167,139,250,.3)", color: "#C4B5FD" } : {}) }}>
                      {v}
                    </button>
                  ))}
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 12px", borderRadius: 10, background: shadow ? "rgba(167,139,250,.08)" : "rgba(255,255,255,.025)", border: `1px solid ${shadow ? "rgba(167,139,250,.2)" : "rgba(255,255,255,.05)"}` }}>
                <Film size={12} color={shadow ? "#A78BFA" : "rgba(226,232,240,.25)"} strokeWidth={1.5} />
                <span style={{ fontSize: 12, color: shadow ? "#A78BFA" : "rgba(226,232,240,.25)" }}>
                  {shadow ? "En cours d'observation…" : "Désactivé"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Vision;
