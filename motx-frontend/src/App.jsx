import { useState, useEffect, useRef } from "react";
import {
  Activity, Zap, Cpu, Bot, BarChart2, Eye,
  CheckCircle, Clock, Database, Mic, Play,
  Server, Layers, WifiOff, Wifi,
  Search, ChevronRight, Send, RefreshCw,
  Shield, Camera, Crosshair, Film, Scan,
  AlertTriangle, Code, Palette, Users, Target, Coffee, RotateCcw
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";
import { API_BASE, WS_BASE } from "./lib/apiConfig";

const USER_ID_KEY = "motx-user-id";
const initialUserId = () => {
  if (typeof window === "undefined") return "web-user";
  const stored = window.localStorage.getItem(USER_ID_KEY);
  if (stored) return stored;
  const generated = `web-user-${Date.now()}`;
  window.localStorage.setItem(USER_ID_KEY, generated);
  return generated;
};

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Outfit', -apple-system, sans-serif; background: #050B18; color: #E2E8F0; overflow: hidden; height: 100vh; }

  .motx-root::before {
    content: ''; position: absolute; inset: 0; pointer-events: none; z-index: 0;
    background-image: radial-gradient(rgba(255,255,255,0.022) 1px, transparent 1px);
    background-size: 28px 28px;
  }

  @keyframes blob1 { 0%,100%{transform:translate(0,0) scale(1)} 40%{transform:translate(50px,-40px) scale(1.1)} 70%{transform:translate(-20px,30px) scale(0.92)} }
  @keyframes blob2 { 0%,100%{transform:translate(0,0) scale(1)} 35%{transform:translate(-50px,40px) scale(1.12)} 65%{transform:translate(30px,-20px) scale(0.9)} }
  @keyframes blob3 { 0%,100%{transform:translate(0,0) scale(1)} 50%{transform:translate(25px,45px) scale(1.07)} }
  @keyframes fadeUp { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.35} }
  @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
  @keyframes ripple { 0%{transform:scale(1);opacity:0.6} 100%{transform:scale(2.2);opacity:0} }

  .nav-item { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:12px; cursor:pointer; transition:all .2s ease; color:rgba(226,232,240,.4); font-size:14px; border:1px solid transparent; user-select:none; }
  .nav-item:hover { background:rgba(255,255,255,.05); color:rgba(226,232,240,.85); transform:translateX(3px); }
  .nav-item.active { background:rgba(96,165,250,.1); border-color:rgba(96,165,250,.18); color:#93C5FD; }

  .glass { background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07); border-radius:20px; backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px); box-shadow:0 8px 32px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.05); transition:border-color .25s, box-shadow .25s; }
  .glass:hover { border-color:rgba(255,255,255,.1); }

  .stat-card { background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.07); border-radius:20px; padding:24px; backdrop-filter:blur(24px); box-shadow:0 8px 32px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.05); transition:all .3s cubic-bezier(.25,.8,.25,1); }
  .stat-card:hover { transform:translateY(-5px); box-shadow:0 24px 56px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.09); border-color:rgba(255,255,255,.11); }

  .btn { display:inline-flex; align-items:center; gap:7px; padding:9px 18px; border-radius:11px; border:1px solid rgba(255,255,255,.09); background:rgba(255,255,255,.05); color:rgba(226,232,240,.75); font-family:'Outfit',sans-serif; font-size:13px; font-weight:500; cursor:pointer; transition:all .2s ease; white-space:nowrap; }
  .btn:hover { background:rgba(255,255,255,.09); border-color:rgba(96,165,250,.28); color:#E2E8F0; transform:translateY(-2px); box-shadow:0 8px 20px rgba(0,0,0,.25); }
  .btn.primary { background:rgba(96,165,250,.13); border-color:rgba(96,165,250,.28); color:#93C5FD; }
  .btn.primary:hover { background:rgba(96,165,250,.22); box-shadow:0 8px 20px rgba(96,165,250,.12); }
  .btn.danger { background:rgba(239,68,68,.1); border-color:rgba(239,68,68,.22); color:#FCA5A5; }
  .btn.danger:hover { background:rgba(239,68,68,.18); }
  .btn.sm { padding:6px 12px; font-size:12px; border-radius:9px; }

  .log-line { margin-bottom:12px; line-height:1.5; }
  .log-line:last-child { margin-bottom:0; }
  .cmd-input { flex:1; background:transparent; border:none; outline:none; color:#E2E8F0; font-family:'JetBrains Mono',monospace; font-size:13px; }
  .cmd-input::placeholder { color:rgba(226,232,240,.22); }
  .shortcut-row { display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,.04); cursor:pointer; transition:background .15s; border-radius:6px; padding:7px 8px; }
  .shortcut-row:hover { background:rgba(255,255,255,.04); }
  .shortcut-row:last-child { border-bottom:none; }

  .cog-btn { display:flex; flex-direction:column; align-items:center; gap:8px; padding:14px 10px; border-radius:14px; border:1px solid rgba(255,255,255,.07); background:rgba(255,255,255,.025); cursor:pointer; transition:all .2s ease; flex:1; }
  .cog-btn:hover { background:rgba(255,255,255,.05); transform:translateY(-2px); }
  .cog-btn.active { border-width:1.5px; }

  .agent-card { background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07); border-radius:18px; padding:22px; backdrop-filter:blur(20px); transition:all .25s ease; animation:fadeUp .5s ease both; }
  .agent-card:hover { border-color:rgba(255,255,255,.12); box-shadow:0 12px 32px rgba(0,0,0,.3); }
  .toggle { width:44px; height:24px; border-radius:12px; border:none; cursor:pointer; transition:all .25s ease; position:relative; flex-shrink:0; }
  .toggle::after { content:''; position:absolute; width:18px; height:18px; border-radius:9px; background:#fff; top:3px; transition:left .25s ease; }
  .toggle.off { background:rgba(255,255,255,.1); }
  .toggle.off::after { left:3px; }
  .toggle.on::after { left:23px; }

  .gaze-group { transition:transform 1.4s cubic-bezier(.4,0,.2,1); }

  ::-webkit-scrollbar { width:4px; }
  ::-webkit-scrollbar-track { background:transparent; }
  ::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:4px; }
`;

const NAV = [
  { id:"dashboard",   label:"Dashboard",   Icon:Activity  },
  { id:"execution",   label:"Exécution",   Icon:Zap       },
  { id:"cognitif",    label:"Cognitif",    Icon:Cpu       },
  { id:"agents",      label:"Agents",      Icon:Bot       },
  { id:"analytiques", label:"Analytiques", Icon:BarChart2 },
  { id:"vision",      label:"Vision",      Icon:Eye       },
];

const DASH_STATS = [
  { label:"Exécutions",   sub:"Total",   value:"0",  Icon:Zap,         color:"#F59E0B", glow:"rgba(245,158,11,.14)",  delay:"0.08s" },
  { label:"Taux Succès",  sub:"Réussite",value:"0%", Icon:CheckCircle, color:"#10B981", glow:"rgba(16,185,129,.13)", delay:"0.16s" },
  { label:"Latence moy.", sub:"Vitesse", value:"—",  Icon:Clock,       color:"#60A5FA", glow:"rgba(96,165,250,.13)",  delay:"0.24s" },
  { label:"Agents Actifs",sub:"En ligne",value:"0",  Icon:Bot,         color:"#A78BFA", glow:"rgba(167,139,250,.13)", delay:"0.32s" },
];

const SERVICES = [
  { label:"FastAPI",     color:"#EF4444", status:"Hors ligne" },
  { label:"ChromaDB",    color:"#EF4444", status:"Hors ligne" },
  { label:"Ollama",      color:"#EF4444", status:"Hors ligne" },
  { label:"Shadow Mode", color:"#6B7280", status:"Inactif"    },
  { label:"Ambient Stream", color:"#6B7280", status:"Inactif" },
  { label:"Eye Tracking",color:"#6B7280", status:"Inactif"    },
  { label:"Voice Engine",color:"#6B7280", status:"Inactif"    },
];

const EXEC_LOG_INIT = [];

const QUICK_CMDS = [
  { label:"Démarrer Shadow",  cmd:"shadow.start()",          color:"#A78BFA" },
  { label:"Chercher fichier", cmd:"nexus.search('')",         color:"#60A5FA" },
  { label:"État cognitif",    cmd:"cognitive.detect()",       color:"#34D399" },
  { label:"Mémoire épisodique",cmd:"rewind.capture()",       color:"#F59E0B" },
  { label:"Lister agents",    cmd:"agents.list()",            color:"#F472B6" },
  { label:"Statut système",   cmd:"system.status()",          color:"#6B7280" },
];

const COG_STATES = [
  { id:"CODING",     label:"Développement", color:"#60A5FA", Icon:Code,    apps:["VSCode","Terminal","GitHub"], adapt:"Dark Pro · notifs OFF · focus max" },
  { id:"CREATIVE",   label:"Création",      color:"#F472B6", Icon:Palette, apps:["Figma","Adobe XD","Procreate"], adapt:"Vibrant · flexibilité max · musique" },
  { id:"MEETING",    label:"Réunion",        color:"#34D399", Icon:Users,   apps:["Zoom","Teams","Google Meet"], adapt:"Mode Pro · notes visibles · micro actif" },
  { id:"FOCUS",      label:"Focus Total",    color:"#A78BFA", Icon:Target,  apps:["Notion","Obsidian","Word"], adapt:"Monochrome · tout caché · DND absolu" },
  { id:"RELAXATION", label:"Détente",        color:"#FBBF24", Icon:Coffee,  apps:["YouTube","Spotify","Netflix"], adapt:"Warm · entertainment · notifs soft" },
];

const AGENTS_INIT = [
  { id:"blackhole", name:"Black Hole",       desc:"Ingestion & vectorisation de fichiers", Icon:Database,   color:"#60A5FA", stat:"0 fichiers",    active:false },
  { id:"shadow",    name:"Shadow Mode",      desc:"Observation silencieuse & workflows",   Icon:Eye,        color:"#A78BFA", stat:"0 captures",    active:false },
  { id:"voice",     name:"Voice Engine",     desc:"Whisper + fallback Google Speech",      Icon:Mic,        color:"#34D399", stat:"0 commandes",   active:false },
  { id:"eyetrack",  name:"Eye Tracking",     desc:"MediaPipe · Look & Do interface",       Icon:Scan,       color:"#F472B6", stat:"Non calibré",   active:false },
  { id:"rewind",    name:"Semantic Rewind",  desc:"Mémoire épisodique temporelle",         Icon:RotateCcw,  color:"#FBBF24", stat:"0 épisodes",    active:false },
];

const WEEK_DATA = [
  { day:"Lun", execs:14, success:13, latency:0.7, agents:2 },
  { day:"Mar", execs:9,  success:8,  latency:1.1, agents:1 },
  { day:"Mer", execs:22, success:20, latency:0.6, agents:3 },
  { day:"Jeu", execs:17, success:15, latency:0.9, agents:2 },
  { day:"Ven", execs:31, success:28, latency:0.5, agents:4 },
  { day:"Sam", execs:8,  success:8,  latency:0.4, agents:2 },
  { day:"Dim", execs:5,  success:4,  latency:1.3, agents:1 },
];

const WEEKDAY_LABELS = ["Dim","Lun","Mar","Mer","Jeu","Ven","Sam"];

const buildWeekAnalytics = (executionLog, agents) => {
  const today = new Date();
  const buckets = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(today);
    date.setDate(today.getDate() - (6 - i));
    return {
      key: date.toISOString().slice(0, 10),
      day: WEEKDAY_LABELS[date.getDay()],
      execs: 0,
      success: 0,
      latency: 0,
      latencyCount: 0,
      agents: 0,
    };
  });

  executionLog.forEach((entry) => {
    const date = entry.createdAt ? new Date(entry.createdAt) : new Date();
    if (isNaN(date.getTime())) return;
    const bucket = buckets.find((b) => b.key === date.toISOString().slice(0, 10));
    if (!bucket) return;

    bucket.execs += 1;
    if (entry.status === "ok") bucket.success += 1;
    const match = entry.out?.match(/(\d+(?:[.,]\d+)?)\s*ms/);
    if (match) {
      bucket.latency += Number(match[1].replace(",", "."));
      bucket.latencyCount += 1;
    }
  });

  const activeAgents = agents.filter((agent) => agent.active).length;
  return buckets.map((bucket) => ({
    day: bucket.day,
    execs: bucket.execs,
    success: bucket.success,
    latency: bucket.latencyCount ? +(bucket.latency / bucket.latencyCount).toFixed(2) : 0,
    agents: activeAgents,
  }));
};

const SLabel = ({ children }) => (
  <div style={{ fontSize:10, color:"rgba(226,232,240,.28)", letterSpacing:"0.15em", textTransform:"uppercase", marginBottom:16 }}>
    {children}
  </div>
);

const ChartTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background:"rgba(8,13,26,.95)", border:"1px solid rgba(255,255,255,.1)", borderRadius:10, padding:"10px 14px", backdropFilter:"blur(20px)" }}>
      <p style={{ fontSize:11, color:"rgba(226,232,240,.4)", marginBottom:6 }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ fontSize:13, color:p.color, fontWeight:500 }}>{p.name} : {p.value}</p>
      ))}
    </div>
  );
};

function DashboardTab({ ambientUpdate, eyeGaze, run, executionLog, services, dashboardMetrics }) {
  const recentExecutions = executionLog.slice(0, 5);
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

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
        {stats.map(({ label, sub, value, Icon, color, glow, delay }) => (
          <div key={label} className="stat-card" style={{ animationDelay: delay }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
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

function ExecutionTab({ run, executionLog, onRunCommand }) {
  const [cmd, setCmd] = useState("");
  const logRef = useRef(null);

  useEffect(() => { logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior:"smooth" }); }, [executionLog]);

  const doRun = (command) => {
    const c = command || cmd.trim();
    if (!c) return;
    setCmd("");
    onRunCommand(c);
  };

  const statusColor = { ok:"#10B981", error:"#EF4444", pending:"#F59E0B" };
  const statusIcon  = { ok:"✓", error:"✕", pending:"●" };

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:14, height:"100%" }}>
      <div style={{ animation:"fadeUp .35s ease both" }}>
        <div style={{ fontSize:10, color:"rgba(226,232,240,.28)", letterSpacing:"0.16em", textTransform:"uppercase", marginBottom:8 }}>Terminal interactif</div>
        <h1 style={{ fontSize:28, fontWeight:600, color:"#E2E8F0", letterSpacing:"-0.02em" }}>Exécution</h1>
      </div>

      <div style={{ display:"flex", gap:14, flex:1, minHeight:0 }}>
        <div className="glass" style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden", minHeight:0 }}>
          <div ref={logRef} style={{ flex:1, overflow:"auto", padding:"22px 26px" }}>
            {executionLog.map(e => (
              <div key={e.id} className="log-line">
                <div style={{ display:"flex", alignItems:"center", gap:10 }}>
                  <span style={{ fontSize:10, color:"rgba(226,232,240,.22)", fontFamily:"monospace", flexShrink:0 }}>{e.time}</span>
                  <span style={{ color:"#60A5FA", fontFamily:"monospace", fontWeight:600 }}>$</span>
                  <span style={{ color:"#E2E8F0", fontFamily:"'JetBrains Mono',monospace", fontSize:13 }}>{e.cmd}</span>
                  <span style={{ color:statusColor[e.status], fontSize:12, marginLeft:4 }}>{statusIcon[e.status]}</span>
                </div>
                <div style={{ color:"rgba(226,232,240,.45)", fontSize:12, fontFamily:"'JetBrains Mono',monospace", marginLeft:62, marginTop:3 }}>
                  → {e.out}
                </div>
              </div>
            ))}
          </div>
          <div style={{ padding:"14px 22px", borderTop:"1px solid rgba(255,255,255,.06)", display:"flex", alignItems:"center", gap:10, background:"rgba(255,255,255,.02)" }}>
            <span style={{ color:"#60A5FA", fontFamily:"monospace", fontSize:16, fontWeight:700 }}>$</span>
            <input
              className="cmd-input"
              value={cmd}
              onChange={e => setCmd(e.target.value)}
              onKeyDown={e => e.key === "Enter" && doRun()}
              placeholder="shadow.start() · nexus.search() · cognitive.detect()…"
            />
            <button className="btn primary sm" onClick={() => doRun()}><Send size={12} strokeWidth={1.5}/></button>
          </div>
        </div>

        <div style={{ width:220, display:"flex", flexDirection:"column", gap:12 }}>
          <div className="glass" style={{ padding:20, flex:1, overflow:"auto" }}>
            <SLabel>Raccourcis</SLabel>
            {QUICK_CMDS.map(({ label, cmd: c }) => (
              <div key={c} className="shortcut-row" onClick={() => doRun(c)}>
                <span style={{ fontSize:12, color:"rgba(226,232,240,.6)" }}>{label}</span>
                <ChevronRight size={12} color="rgba(226,232,240,.2)" strokeWidth={1.5}/>
              </div>
            ))}
          </div>
          <div className="glass" style={{ padding:20 }}>
            <SLabel>Historique</SLabel>
            <div style={{ display:"flex", justifyContent:"space-between", marginBottom:8 }}>
              <span style={{ fontSize:12, color:"rgba(226,232,240,.4)" }}>Total</span>
              <span style={{ fontSize:13, color:"#E2E8F0", fontFamily:"monospace" }}>{executionLog.length}</span>
            </div>
            <div style={{ display:"flex", justifyContent:"space-between", marginBottom:8 }}>
              <span style={{ fontSize:12, color:"rgba(226,232,240,.4)" }}>Succès</span>
              <span style={{ fontSize:13, color:"#10B981", fontFamily:"monospace" }}>{executionLog.filter(l=>l.status==="ok").length}</span>
            </div>
            <div style={{ display:"flex", justifyContent:"space-between" }}>
              <span style={{ fontSize:12, color:"rgba(226,232,240,.4)" }}>Erreurs</span>
              <span style={{ fontSize:13, color:"#EF4444", fontFamily:"monospace" }}>{executionLog.filter(l=>l.status==="error").length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function CognitifTab({ ambientUpdate, eyeGaze, connected, ambientConnected, eyeConnected }) {
  const [active, setActive] = useState("CODING");
  const current = COG_STATES.find(s => s.id === active);

  useEffect(() => {
    if (ambientUpdate?.cognitive_state) {
      const candidate = ambientUpdate.cognitive_state.toString().toUpperCase();
      if (COG_STATES.some(s => s.id === candidate)) {
        setActive(candidate);
      }
    }
  }, [ambientUpdate]);

  const detectedState = ambientUpdate?.cognitive_state ? ambientUpdate.cognitive_state.toString().toUpperCase() : "N/A";
  const gazePosition = eyeGaze ? `x:${Math.round(eyeGaze.x ?? 0)} y:${Math.round(eyeGaze.y ?? 0)}${eyeGaze.z != null ? ` z:${Math.round(eyeGaze.z)}` : ''}` : "Aucun flux";

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
      <div style={{ animation:"fadeUp .35s ease both" }}>
        <div style={{ fontSize:10, color:"rgba(226,232,240,.28)", letterSpacing:"0.16em", textTransform:"uppercase", marginBottom:8 }}>Liquid OS · Adaptation cognitive</div>
        <h1 style={{ fontSize:28, fontWeight:600, color:"#E2E8F0", letterSpacing:"-0.02em" }}>Cognitif</h1>
        <div style={{ display:"flex", flexWrap:"wrap", gap:10, marginTop:12 }}>
          {[
            { label: "FastAPI", active: connected, color: connected ? "#10B981" : "#EF4444", value: connected ? "Connecté" : "Hors ligne" },
            { label: "Ambient", active: ambientConnected, color: ambientConnected ? "#10B981" : "#F59E0B", value: ambientConnected ? "Flux actif" : "En attente" },
            { label: "Eye", active: eyeConnected, color: eyeConnected ? "#10B981" : "#F59E0B", value: eyeConnected ? "Tracking actif" : "En attente" },
          ].map(({ label, active, color, value }) => (
            <div key={label} style={{ display:"flex", alignItems:"center", gap:8, padding:"10px 14px", borderRadius:12, background: active ? `${color}15` : "rgba(255,255,255,.05)", border:`1px solid ${active ? `${color}30` : "rgba(255,255,255,.08)"}`, color: active ? color : "rgba(226,232,240,.55)", fontSize:12 }}>
              <span style={{ width:8, height:8, borderRadius:"50%", background: color }} />
              <strong>{label}:</strong> {value}
            </div>
          ))}
        </div>
      </div>

      <div style={{ display:"flex", gap:10, flexWrap:"wrap" }}>
        {COG_STATES.map(({ id, label, color, Icon }) => {
          const on = id === active;
          return (
            <div
              key={id}
              className={`cog-btn${on ? " active" : ""}`}
              onClick={() => setActive(id)}
              style={on ? { borderColor: color, background: `${color}12` } : {}}
            >
              <div style={{
                width:36, height:36, borderRadius:10, display:"flex", alignItems:"center", justifyContent:"center",
                background: on ? `${color}20` : "rgba(255,255,255,.04)",
                border: `1px solid ${on ? color+"44" : "rgba(255,255,255,.06)"}`,
                transition:"all .2s"
              }}>
                <Icon size={16} color={on ? color : "rgba(226,232,240,.35)"} strokeWidth={1.5}/>
              </div>
              <span style={{ fontSize:11, color: on ? color : "rgba(226,232,240,.4)", fontWeight: on ? 500 : 400, textAlign:"center" }}>{label}</span>
            </div>
          );
        })}
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:14, flex:1 }}>
        <div className="glass" style={{ padding:28, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:20 }}>
          <div style={{ position:"relative", width:140, height:140 }}>
            <svg viewBox="0 0 140 140" style={{ width:140, height:140, position:"absolute", inset:0 }}>
              <circle cx="70" cy="70" r="58" fill="none" stroke="rgba(255,255,255,.05)" strokeWidth="8"/>
              <circle
                cx="70" cy="70" r="58" fill="none"
                stroke={current.color}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 58 * 0.72} ${2 * Math.PI * 58}`}
                style={{ transform:"rotate(-90deg)", transformOrigin:"70px 70px", filter:`drop-shadow(0 0 6px ${current.color}66)`, transition:"stroke .4s ease, filter .4s ease" }}
              />
            </svg>
            <div style={{ position:"absolute", inset:0, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:4 }}>
              <current.Icon size={24} color={current.color} strokeWidth={1.5}/>
              <span style={{ fontSize:11, color:current.color, fontWeight:600, letterSpacing:"0.08em", textTransform:"uppercase", transition:"color .3s" }}>{current.id}</span>
            </div>
          </div>

          <div style={{ width:"100%", textAlign:"center" }}>
            <div style={{ fontSize:11, color:"rgba(226,232,240,.3)", marginBottom:8 }}>Confiance détection</div>
            <div style={{ height:6, borderRadius:3, background:"rgba(255,255,255,.06)", overflow:"hidden" }}>
              <div style={{
                height:"100%", borderRadius:3, width:"72%",
                background:`linear-gradient(90deg, ${current.color}88, ${current.color})`,
                transition:"background .4s ease",
                boxShadow:`0 0 8px ${current.color}44`
              }}/>
            </div>
            <div style={{ fontSize:12, color:current.color, marginTop:6, fontFamily:"monospace", fontWeight:600, transition:"color .3s" }}>72%</div>
          </div>
        </div>

        <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
          <div className="glass" style={{ padding:22, flex:1 }}>
            <SLabel>Applications détectées</SLabel>
            <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
              {current.apps.map(app => (
                <div key={app} style={{ display:"flex", alignItems:"center", gap:10, padding:"8px 12px", borderRadius:10, background:"rgba(255,255,255,.03)", border:"1px solid rgba(255,255,255,.05)" }}>
                  <div style={{ width:7, height:7, borderRadius:"50%", background:current.color, boxShadow:`0 0 6px ${current.color}66` }}/>
                  <span style={{ fontSize:13, color:"rgba(226,232,240,.65)" }}>{app}</span>
                </div>
              ))}
            </div>
            <div style={{ marginTop:16, padding:14, borderRadius:12, background:"rgba(255,255,255,.04)", border:"1px solid rgba(255,255,255,.06)" }}>
              <div style={{ fontSize:11, color:"rgba(226,232,240,.4)", marginBottom:8 }}>Détection en direct</div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
                <div style={{ fontSize:13, color:"rgba(226,232,240,.75)" }}><strong>État</strong><br/>{detectedState}</div>
                <div style={{ fontSize:13, color:"rgba(226,232,240,.75)" }}><strong>Gaze</strong><br/>{gazePosition}</div>
              </div>
            </div>
          </div>
          <div className="glass" style={{ padding:22, flex:1 }}>
            <SLabel>Adaptations appliquées</SLabel>
            <div style={{ padding:"12px 16px", borderRadius:12, background:`${current.color}0d`, border:`1px solid ${current.color}22`, transition:"all .3s" }}>
              <div style={{ display:"flex", alignItems:"flex-start", gap:10 }}>
                <Shield size={14} color={current.color} strokeWidth={1.5} style={{ marginTop:2, flexShrink:0 }}/>
                <span style={{ fontSize:13, color:"rgba(226,232,240,.7)", lineHeight:1.5 }}>{current.adapt}</span>
              </div>
            </div>
            <div style={{ marginTop:14 }}>
              <button
                className="btn primary"
                style={{ width:"100%", justifyContent:"center" }}
                onClick={() => {
                  if (ambientUpdate?.cognitive_state) {
                    setActive(ambientUpdate.cognitive_state.toString().toUpperCase());
                  }
                }}
                disabled={!ambientUpdate?.cognitive_state}
              >
                <RefreshCw size={12} strokeWidth={1.5}/> Appliquer l'état détecté
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AgentsTab({ agents, onToggleAgent }) {
  const activeCount = agents.filter(a => a.active).length;

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
      <div style={{ display:"flex", alignItems:"flex-end", justifyContent:"space-between", animation:"fadeUp .35s ease both" }}>
        <div>
          <div style={{ fontSize:10, color:"rgba(226,232,240,.28)", letterSpacing:"0.16em", textTransform:"uppercase", marginBottom:8 }}>Gestionnaire d'agents</div>
          <h1 style={{ fontSize:28, fontWeight:600, color:"#E2E8F0", letterSpacing:"-0.02em" }}>Agents</h1>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:8, padding:"8px 16px", borderRadius:12, background:"rgba(255,255,255,.04)", border:"1px solid rgba(255,255,255,.07)" }}>
          <div style={{ width:7, height:7, borderRadius:"50%", background: activeCount > 0 ? "#10B981" : "#6B7280", ...(activeCount>0?{animation:"pulse 2s ease infinite"}:{}) }}/>
          <span style={{ fontSize:13, color:"rgba(226,232,240,.6)" }}>{activeCount} actif{activeCount!==1?"s":""}</span>
        </div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        {agents.map(({ id, name, desc, Icon, color, stat, active }, i) => (
          <div key={id} className="agent-card" style={{ animationDelay:`${i * 0.07}s`, ...(active?{ borderColor:`${color}28`, boxShadow:`0 0 20px ${color}0d` }:{}) }}>
            <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", marginBottom:16 }}>
              <div style={{ display:"flex", alignItems:"center", gap:12 }}>
                <div style={{
                  width:40, height:40, borderRadius:12,
                  background: active ? `${color}20` : "rgba(255,255,255,.05)",
                  border: `1px solid ${active ? color+"40" : "rgba(255,255,255,.07)"}`,
                  display:"flex", alignItems:"center", justifyContent:"center",
                  transition:"all .3s ease"
                }}>
                  <Icon size={18} color={active ? color : "rgba(226,232,240,.35)"} strokeWidth={1.5}/>
                </div>
                <div>
                  <div style={{ fontSize:14, fontWeight:500, color:"#E2E8F0", marginBottom:2 }}>{name}</div>
                  <div style={{ fontSize:11, color:"rgba(226,232,240,.35)" }}>{desc}</div>
                </div>
              </div>
              <button
                className={`toggle ${active ? "on" : "off"}`}
                onClick={() => onToggleAgent(id)}
                style={active ? { background:color } : {}}
              />
            </div>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", paddingTop:12, borderTop:"1px solid rgba(255,255,255,.05)" }}>
              <span style={{ fontSize:12, fontFamily:"'JetBrains Mono',monospace", color: active ? color : "rgba(226,232,240,.28)" }}>
                {stat}
              </span>
              <span style={{ fontSize:11, padding:"3px 8px", borderRadius:6, background: active ? `${color}18` : "rgba(255,255,255,.04)", color: active ? color : "rgba(226,232,240,.28)", fontWeight:500 }}>
                {active ? "En ligne" : "Hors ligne"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalytiquesTab({ executionLog, agents, ambientUpdate, eyeGaze, services, connected, ambientConnected, eyeConnected }) {
  const weekData = buildWeekAnalytics(executionLog, agents);
  const total = executionLog.length;
  const successRate = total ? Math.round(executionLog.filter((e) => e.status === 'ok').length / total * 100) : 0;
  const allLatencies = executionLog.map((entry) => {
    const match = entry.out?.match(/(\d+(?:[.,]\d+)?)\s*ms/);
    return match ? Number(match[1].replace(",", ".")) : null;
  }).filter((value) => value != null);
  const avgLatency = allLatencies.length ? (allLatencies.reduce((s, v) => s + v, 0) / allLatencies.length).toFixed(2) : '—';
  const activeAgents = agents.filter((agent) => agent.active).length;
  const workflowCount = ambientUpdate?.active_workflows ?? 0;
  const cognitiveState = ambientUpdate?.cognitive_state ?? 'Inconnu';
  const gazePosition = eyeGaze ? `x:${Math.round(eyeGaze.x)} y:${Math.round(eyeGaze.y)}` : 'Aucun';
  const fastApiStatus = connected ? 'En ligne' : 'Hors ligne';
  const ollamaStatus = services.find((s) => s.label === 'Ollama')?.status ?? 'Inconnu';
  const chromaStatus = services.find((s) => s.label === 'ChromaDB')?.status ?? 'Inconnu';

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
      <div style={{ animation:"fadeUp .35s ease both" }}>
        <div style={{ fontSize:10, color:"rgba(226,232,240,.28)", letterSpacing:"0.16em", textTransform:"uppercase", marginBottom:8 }}>7 derniers jours</div>
        <h1 style={{ fontSize:28, fontWeight:600, color:"#E2E8F0", letterSpacing:"-0.02em" }}>Analytiques</h1>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:12 }}>
        {[
          { label:"Exécutions totales", value:total,          color:"#60A5FA", Icon:Zap,         sub:"cette semaine" },
          { label:"Taux de succès",     value:`${successRate}%`, color:"#10B981", Icon:CheckCircle, sub:"en moyenne" },
          { label:"Latence moyenne",    value:`${avgLatency}s`,  color:"#F59E0B", Icon:Clock,       sub:"par requête" },
        ].map(({ label, value, color, Icon }) => (
          <div key={label} className="glass" style={{ padding:"20px 22px", display:"flex", alignItems:"center", gap:16 }}>
            <div style={{ width:40, height:40, borderRadius:11, background:`${color}18`, border:`1px solid ${color}28`, display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
              <Icon size={16} color={color} strokeWidth={1.5}/>
            </div>
            <div>
              <div style={{ fontSize:22, fontWeight:600, color:"#E2E8F0", fontFamily:"'JetBrains Mono',monospace", letterSpacing:"-0.02em" }}>{value}</div>
              <div style={{ fontSize:11, color:"rgba(226,232,240,.35)", marginTop:2 }}>{label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="glass" style={{ padding:"22px 22px 14px" }}>
        <SLabel>Exécutions · 7 jours</SLabel>
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={weekData} margin={{ top:4, right:4, bottom:0, left:-20 }}>
            <defs>
              <linearGradient id="gExec" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#60A5FA" stopOpacity={0.25}/>
                <stop offset="95%" stopColor="#60A5FA" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="gSucc" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
            <XAxis dataKey="day" tick={{ fill:"rgba(226,232,240,.3)", fontSize:11 }} axisLine={false} tickLine={false}/>
            <YAxis tick={{ fill:"rgba(226,232,240,.3)", fontSize:11 }} axisLine={false} tickLine={false}/>
            <Tooltip content={<ChartTip/>}/>
            <Area type="monotone" dataKey="execs"   name="Exécutions" stroke="#60A5FA" strokeWidth={2} fill="url(#gExec)" dot={false}/>
            <Area type="monotone" dataKey="success" name="Succès"      stroke="#10B981" strokeWidth={2} fill="url(#gSucc)" dot={false}/>
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="glass" style={{ padding:"22px 22px 14px" }}>
          <SLabel>Latence (s)</SLabel>
          <ResponsiveContainer width="100%" height={120}>
            <AreaChart data={weekData} margin={{ top:4, right:4, bottom:0, left:-20 }}>
              <defs>
                <linearGradient id="gLat" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.25}/>
                  <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
              <XAxis dataKey="day" tick={{ fill:"rgba(226,232,240,.3)", fontSize:10 }} axisLine={false} tickLine={false}/>
              <YAxis tick={{ fill:"rgba(226,232,240,.3)", fontSize:10 }} axisLine={false} tickLine={false}/>
              <Tooltip content={<ChartTip/>}/>
              <Area type="monotone" dataKey="latency" name="Latence" stroke="#F59E0B" strokeWidth={2} fill="url(#gLat)" dot={false}/>
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="glass" style={{ padding:"22px 22px 14px" }}>
          <SLabel>Agents actifs / jour</SLabel>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={weekData} margin={{ top:4, right:4, bottom:0, left:-20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false}/>
              <XAxis dataKey="day" tick={{ fill:"rgba(226,232,240,.3)", fontSize:10 }} axisLine={false} tickLine={false}/>
              <YAxis tick={{ fill:"rgba(226,232,240,.3)", fontSize:10 }} axisLine={false} tickLine={false}/>
              <Tooltip content={<ChartTip/>}/>
              <Bar dataKey="agents" name="Agents" fill="#A78BFA" radius={[4,4,0,0]} fillOpacity={0.75}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="glass" style={{ padding:"22px 22px 14px" }}>
        <SLabel>Statut live</SLabel>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
          {[
            { label: 'FastAPI', value: fastApiStatus, color: connected ? '#10B981' : '#EF4444' },
            { label: 'ChromaDB', value: chromaStatus, color: chromaStatus === 'En ligne' ? '#10B981' : '#EF4444' },
            { label: 'Ollama', value: ollamaStatus, color: ollamaStatus === 'En ligne' ? '#10B981' : '#EF4444' },
            { label: 'Ambient', value: ambientConnected ? 'Actif' : 'Inactif', color: ambientConnected ? '#10B981' : '#6B7280' },
            { label: 'Eye Tracking', value: eyeConnected ? 'Actif' : 'Inactif', color: eyeConnected ? '#10B981' : '#6B7280' },
            { label: 'Agents actifs', value: `${activeAgents}`, color: activeAgents ? '#10B981' : '#6B7280' }
          ].map(({ label, value, color }) => (
            <div key={label} style={{ display:'flex', flexDirection:'column', gap:4, padding:12, borderRadius:12, background:'rgba(255,255,255,.03)', border:'1px solid rgba(255,255,255,.05)' }}>
              <span style={{ fontSize:10, color:'rgba(226,232,240,.4)', textTransform:'uppercase' }}>{label}</span>
              <span style={{ fontSize:15, color, fontWeight:600 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="glass" style={{ padding:"22px 22px 14px" }}>
        <SLabel>Statut de l'environnement</SLabel>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
          <div style={{ padding:12, borderRadius:12, background:'rgba(255,255,255,.03)', border:'1px solid rgba(255,255,255,.05)' }}>
            <div style={{ fontSize:12, color:'rgba(226,232,240,.4)', marginBottom:6 }}>État cognitif</div>
            <div style={{ fontSize:15, fontWeight:600, color:'#93C5FD' }}>{cognitiveState}</div>
          </div>
          <div style={{ padding:12, borderRadius:12, background:'rgba(255,255,255,.03)', border:'1px solid rgba(255,255,255,.05)' }}>
            <div style={{ fontSize:12, color:'rgba(226,232,240,.4)', marginBottom:6 }}>Position regard</div>
            <div style={{ fontSize:15, fontWeight:600, color:'#60A5FA' }}>{gazePosition}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function VisionTab() {
  const [gaze, setGaze]         = useState({ x:50, y:32 });
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
    const pts = [[20,20],[50,20],[80,20],[20,50],[50,50],[80,50],[20,80],[50,80],[80,80]];
    let i = 0;
    const t = setInterval(() => {
      const p = pts[i % pts.length];
      setGaze({ x:5 + p[0]*0.9, y:5 + p[1]*0.55 });
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
    <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
      <div style={{ animation:"fadeUp .35s ease both" }}>
        <div style={{ fontSize:10, color:"rgba(226,232,240,.28)", letterSpacing:"0.16em", textTransform:"uppercase", marginBottom:8 }}>Eye Tracking · Shadow Mode</div>
        <h1 style={{ fontSize:28, fontWeight:600, color:"#E2E8F0", letterSpacing:"-0.02em" }}>Vision</h1>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1.4fr 1fr", gap:14 }}>
        <div className="glass" style={{ padding:24 }}>
          <SLabel>Suivi oculaire — aperçu écran</SLabel>
          <div style={{ borderRadius:14, overflow:"hidden", background:"#020509", border:"1px solid rgba(255,255,255,.06)", position:"relative" }}>
            <svg viewBox="0 0 100 62" style={{ width:"100%", display:"block" }}>
              <defs>
                <radialGradient id="gazeGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.6"/>
                  <stop offset="100%" stopColor="#60A5FA" stopOpacity="0"/>
                </radialGradient>
              </defs>
              {[25,50,75].map(x => <line key={x} x1={x} y1="0" x2={x} y2="62" stroke="rgba(255,255,255,.03)" strokeWidth="0.3"/>)}
              {[20,40,55].map(y => <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="rgba(255,255,255,.03)" strokeWidth="0.3"/>)}
              {tracking && <>
                <line x1={gaze.x} y1="0" x2={gaze.x} y2="62" stroke="rgba(96,165,250,.12)" strokeWidth="0.4"/>
                <line x1="0" y1={gaze.y} x2="100" y2={gaze.y} stroke="rgba(96,165,250,.12)" strokeWidth="0.4"/>
              </>}
              <g className="gaze-group" style={{ transform:`translate(${gaze.x}px, ${gaze.y}px)` }}>
                {tracking ? <>
                  <circle r="12" fill="url(#gazeGlow)" opacity="0.4"/>
                  <circle r="6" fill="none" stroke="rgba(96,165,250,.3)" strokeWidth="0.5"/>
                  <circle r="2.8" fill={calibrated ? "#60A5FA" : "#F59E0B"} style={{ filter:`drop-shadow(0 0 4px ${calibrated?"#60A5FA":"#F59E0B"})` }}/>
                  <line x1="-5" y1="0" x2="-2.5" y2="0" stroke="rgba(96,165,250,.8)" strokeWidth="0.5"/>
                  <line x1="2.5" y1="0" x2="5" y2="0" stroke="rgba(96,165,250,.8)" strokeWidth="0.5"/>
                  <line x1="0" y1="-5" x2="0" y2="-2.5" stroke="rgba(96,165,250,.8)" strokeWidth="0.5"/>
                  <line x1="0" y1="2.5" x2="0" y2="5" stroke="rgba(96,165,250,.8)" strokeWidth="0.5"/>
                </> : <circle r="2" fill="rgba(226,232,240,.1)"/>}
              </g>
            </svg>
          </div>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginTop:14 }}>
            <div style={{ display:"flex", gap:14 }}>
              {[{ l:"X", v:tracking?`${Math.round(gaze.x)}%`:"—" }, { l:"Y", v:tracking?`${Math.round(gaze.y)}%`:"—" }].map(({l,v}) => (
                <div key={l} style={{ fontSize:12, color:"rgba(226,232,240,.4)", fontFamily:"monospace" }}>
                  <span>{l}: </span>
                  <span style={{ color: tracking ? "#60A5FA" : "rgba(226,232,240,.2)" }}>{v}</span>
                </div>
              ))}
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:6 }}>
              <div style={{ width:6, height:6, borderRadius:"50%", background: tracking ? "#10B981" : "#6B7280", ...(tracking?{animation:"pulse 2s ease infinite"}:{}) }}/>
              <span style={{ fontSize:11, color: tracking ? "#10B981" : "rgba(226,232,240,.3)" }}>{tracking ? "Actif" : "Inactif"}</span>
            </div>
          </div>
        </div>

        <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
          <div className="glass" style={{ padding:22, flex:1 }}>
            <SLabel>Eye Tracking</SLabel>
            <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"10px 14px", borderRadius:11, background:"rgba(255,255,255,.03)", border:"1px solid rgba(255,255,255,.06)" }}>
                <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                  <Crosshair size={13} color="rgba(226,232,240,.4)" strokeWidth={1.5}/>
                  <span style={{ fontSize:13, color:"rgba(226,232,240,.55)" }}>Tracking</span>
                </div>
                <button
                  className={`toggle ${tracking ? "on" : "off"}`}
                  onClick={() => setTracking(t => !t)}
                  style={tracking ? { background:"#60A5FA" } : {}}
                />
              </div>

              <div style={{
                padding:"10px 14px", borderRadius:11,
                background: calibrated ? "rgba(16,185,129,.08)" : "rgba(245,158,11,.07)",
                border: `1px solid ${calibrated ? "rgba(16,185,129,.2)" : "rgba(245,158,11,.2)"}`
              }}>
                <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:8 }}>
                  {calibrated
                    ? <CheckCircle size={12} color="#10B981" strokeWidth={1.5}/>
                    : <AlertTriangle size={12} color="#F59E0B" strokeWidth={1.5}/>
                  }
                  <span style={{ fontSize:12, color: calibrated ? "#10B981" : "#F59E0B", fontWeight:500 }}>
                    {calibrating ? "Calibration en cours…" : calibrated ? "Calibré (9 pts)" : "Non calibré"}
                  </span>
                </div>
                <button
                  className="btn sm"
                  onClick={calibrate}
                  disabled={calibrating}
                  style={{ width:"100%", justifyContent:"center", opacity: calibrating ? 0.5 : 1 }}
                >
                  <Scan size={11} strokeWidth={1.5}/> {calibrating ? "…" : "Lancer calibration"}
                </button>
              </div>
            </div>
          </div>

          <div className="glass" style={{ padding:22, flex:1 }}>
            <SLabel>Shadow Mode</SLabel>
            <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"10px 14px", borderRadius:11, background:"rgba(255,255,255,.03)", border:"1px solid rgba(255,255,255,.06)" }}>
                <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                  <Camera size={13} color="rgba(226,232,240,.4)" strokeWidth={1.5}/>
                  <span style={{ fontSize:13, color:"rgba(226,232,240,.55)" }}>Observation</span>
                </div>
                <button
                  className={`toggle ${shadow ? "on" : "off"}`}
                  onClick={() => setShadow(s => !s)}
                  style={shadow ? { background:"#A78BFA" } : {}}
                />
              </div>
              <div style={{ padding:"10px 14px", borderRadius:11, background:"rgba(255,255,255,.03)", border:"1px solid rgba(255,255,255,.06)" }}>
                <div style={{ fontSize:11, color:"rgba(226,232,240,.3)", marginBottom:6 }}>Intervalle capture</div>
                <div style={{ display:"flex", gap:6 }}>
                  {["2s", "5s", "10s"].map(v => (
                    <button key={v} className="btn sm" style={{ flex:1, justifyContent:"center", ...(v==="2s"?{background:"rgba(167,139,250,.15)", borderColor:"rgba(167,139,250,.3)", color:"#C4B5FD"}:{} ) }}>
                      {v}
                    </button>
                  ))}
                </div>
              </div>
              <div style={{ display:"flex", alignItems:"center", gap:6, padding:"8px 12px", borderRadius:10, background: shadow ? "rgba(167,139,250,.08)" : "rgba(255,255,255,.025)", border:`1px solid ${shadow ? "rgba(167,139,250,.2)" : "rgba(255,255,255,.05)"}` }}>
                <Film size={12} color={shadow ? "#A78BFA" : "rgba(226,232,240,.25)"} strokeWidth={1.5}/>
                <span style={{ fontSize:12, color: shadow ? "#A78BFA" : "rgba(226,232,240,.25)" }}>
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

const TABS = { dashboard:DashboardTab, execution:ExecutionTab, cognitif:CognitifTab, agents:AgentsTab, analytiques:AnalytiquesTab, vision:VisionTab };

export default function App() {
  const [active, setActive] = useState("dashboard");
  const [connected, setConnected] = useState(false);
  const [ambientConnected, setAmbientConnected] = useState(false);
  const [eyeConnected, setEyeConnected] = useState(false);
  const [ambientUpdate, setAmbientUpdate] = useState(null);
  const [eyeGaze, setEyeGaze] = useState(null);
  const [executionLog, setExecutionLog] = useState(EXEC_LOG_INIT);
  const [agents, setAgents] = useState(AGENTS_INIT);
  const [services, setServices] = useState(SERVICES);
  const [dashboardMetrics, setDashboardMetrics] = useState({
    totalExecutions: 0,
    successRate: 0,
    averageSpeed: 0,
    activeAgents: 0
  });
  const [userId] = useState(initialUserId);
  const genericSocketRef = useRef(null);

  useEffect(() => {
    const style = document.createElement("style");
    style.textContent = CSS;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/history?limit=20&user_id=${encodeURIComponent(userId)}`);
        if (!response.ok) {
          throw new Error(`Backend non accessible (${response.status})`);
        }
        const payload = await response.json();
        if (Array.isArray(payload?.history)) {
          setExecutionLog(payload.history.map((entry, index) => ({
            id: entry.id ?? `history-${index}`,
            cmd: entry.command ?? entry.instruction ?? entry.cmd ?? "Historique",
            status: entry.status ?? (entry.success ? "ok" : "error"),
            time: entry.time ?? (entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString("fr", { hour12: false }) : ""),
            out: entry.out ?? entry.message ?? JSON.stringify(entry.data ?? entry, null, 2),
            createdAt: entry.createdAt ?? entry.timestamp ?? new Date().toISOString()
          })));
        }
      } catch (error) {
        console.warn("Impossible de charger l'historique depuis le backend", error);
      }
    };

    fetchHistory();
  }, [userId]);

  useEffect(() => {
    const userKey = userId || "web-user";
    const createSocket = ({ url, onOpen, onMessage, onClose }) => {
      try {
        const socket = new WebSocket(url);
        socket.onopen = onOpen;
        socket.onmessage = onMessage;
        socket.onclose = onClose;
        socket.onerror = onClose;
        return socket;
      } catch (error) {
        console.warn(`WebSocket error on ${url}:`, error);
        return null;
      }
    };

    const genericWs = createSocket({
      url: `${WS_BASE}/${userKey}`,
      onOpen: () => setConnected(true),
      onMessage: (event) => {
        try {
          const payload = JSON.parse(event.data);
          console.log('Generic WS:', payload);
          if (payload?.type === 'execution_result') {
            const entry = {
              id: Date.now(),
              cmd: payload.command || 'unknown',
              status: payload.success ? 'ok' : 'error',
              time: new Date().toLocaleTimeString('fr', { hour12: false }),
              out: payload.message || (payload.success ? 'Résultat reçu' : 'Erreur du service'),
              createdAt: new Date().toISOString()
            };
            setExecutionLog((prev) => [entry, ...prev].slice(0, 50));
          }
          if (payload?.type === 'agent_update' && payload.agent_id) {
            setAgents((prev) => prev.map((agent) =>
              agent.id === payload.agent_id
                ? { ...agent, active: payload.active ?? agent.active, stat: payload.stat || agent.stat }
                : agent
            ));
          }
            if (payload?.type === 'chroma_status') {
              const chromaStatus = payload.payload?.status === 'ok';
              setServices((prev) => prev.map((s) => s.label === 'ChromaDB'
                ? { ...s, color: chromaStatus ? '#10B981' : '#EF4444', status: chromaStatus ? 'En ligne' : 'Hors ligne' }
                : s
              ));
            }
        } catch {
          console.warn('Invalid generic payload');
        }
      },
      onClose: () => setConnected(false)
    });
    genericSocketRef.current = genericWs;

    const ambientWs = createSocket({
      url: `${WS_BASE}/ambient/${userKey}`,
      onOpen: () => setAmbientConnected(true),
      onMessage: (event) => {
        try { const payload = JSON.parse(event.data); setAmbientUpdate(payload); } catch { console.warn('Invalid ambient payload'); }
      },
      onClose: () => setAmbientConnected(false)
    });

    const eyeWs = createSocket({
      url: `${WS_BASE}/eye/${userKey}`,
      onOpen: () => setEyeConnected(true),
      onMessage: (event) => {
        try { const payload = JSON.parse(event.data); setEyeGaze(payload); } catch { console.warn('Invalid eye payload'); }
      },
      onClose: () => setEyeConnected(false)
    });

    return () => {
      [genericWs, ambientWs, eyeWs].forEach(ws => { if (ws && ws.readyState === WebSocket.OPEN) ws.close(); });
    };
  }, [userId]);

  useEffect(() => {
    const fetchDashboardMetrics = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/analytics/dashboard`);
        if (!response.ok) throw new Error(`Backend returned ${response.status}`);
        const payload = await response.json();
        const analytics = payload.analytics || payload;
        const overview = analytics.overview || analytics.analytics || {};
        const performance = analytics.performance || analytics.analytics || {};

        const totalExecutions = overview.total_executions ?? overview.total_automations ?? executionLog.length;
        const successRate = overview.success_rate ?? performance.success_rate ?? 0;
        const averageSpeed = overview.average_speed_seconds ?? performance.average_execution_time ?? 0;
        const activeAgents = overview.active_agents ?? overview.active_workflows ?? agents.filter((agent) => agent.active).length;

        setDashboardMetrics({
          totalExecutions,
          successRate,
          averageSpeed,
          activeAgents
        });
      } catch (error) {
        console.warn('Impossible de charger les métriques du dashboard', error);
        const successful = executionLog.filter((e) => e.status === 'ok').length;
        setDashboardMetrics({
          totalExecutions: executionLog.length,
          successRate: executionLog.length ? (successful / executionLog.length) * 100 : 0,
          averageSpeed: 0,
          activeAgents: agents.filter((agent) => agent.active).length
        });
      }
    };

    fetchDashboardMetrics();
  }, [executionLog, agents, connected]);

  // Poll /api/status to get real ChromaDB status instead of relying on `connected` proxy
  useEffect(() => {
    let mounted = true;
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status`);
        if (!res.ok) throw new Error(`status ${res.status}`);
        const payload = await res.json();
        const chromaStatus = payload?.services?.chroma?.status === 'ok';
        if (!mounted) return;
        setServices((prev) => prev.map((s) => s.label === 'ChromaDB'
          ? { ...s, color: chromaStatus ? '#10B981' : '#EF4444', status: chromaStatus ? 'En ligne' : 'Hors ligne' }
          : s
        ));
      } catch (err) {
        if (!mounted) return;
        setServices((prev) => prev.map((s) => s.label === 'ChromaDB'
          ? { ...s, color: '#EF4444', status: 'Hors ligne' }
          : s
        ));
      }
    };

    checkStatus();
    const iv = setInterval(checkStatus, 10000);
    return () => { mounted = false; clearInterval(iv); };
  }, [connected]);

  const handleRunCommand = (command) => {
    const entry = {
      id: Date.now(),
      cmd: command,
      status: 'pending',
      time: new Date().toLocaleTimeString('fr', { hour12: false }),
      out: 'En cours…',
      createdAt: new Date().toISOString()
    };
    setExecutionLog((prev) => [...prev, entry]);
    if (genericSocketRef.current && genericSocketRef.current.readyState === WebSocket.OPEN) {
      genericSocketRef.current.send(JSON.stringify({ type: 'run_command', command }));
    }
  };

  const handleToggleAgent = (agentId) => {
    setAgents((prev) => prev.map((agent) =>
      agent.id === agentId ? { ...agent, active: !agent.active } : agent
    ));
  };

  useEffect(() => {
    const shadowActive = agents.find((agent) => agent.id === "shadow")?.active;
    const voiceActive = agents.find((agent) => agent.id === "voice")?.active;

    setServices(SERVICES.map(service => {
      if (service.label === "FastAPI") {
        return { ...service, color: connected ? "#10B981" : "#EF4444", status: connected ? "En ligne" : "Hors ligne" };
      }
      if (service.label === "Ambient Stream") {
        return { ...service, color: ambientConnected ? "#10B981" : "#6B7280", status: ambientConnected ? "Actif" : "Inactif" };
      }
      if (service.label === "Eye Tracking") {
        return { ...service, color: eyeConnected ? "#10B981" : "#6B7280", status: eyeConnected ? "Actif" : "Inactif" };
      }
      if (service.label === "Ollama") {
        return { ...service, color: connected ? "#10B981" : "#EF4444", status: connected ? "En ligne" : "Hors ligne" };
      }
      if (service.label === "ChromaDB") {
        return { ...service, color: connected ? "#10B981" : "#EF4444", status: connected ? "En ligne" : "Hors ligne" };
      }
      if (service.label === "Shadow Mode") {
        return { ...service, color: shadowActive ? "#10B981" : "#6B7280", status: shadowActive ? "Actif" : "Inactif" };
      }
      if (service.label === "Voice Engine") {
        return { ...service, color: voiceActive ? "#10B981" : "#6B7280", status: voiceActive ? "Actif" : "Inactif" };
      }
      return service;
    }));
  }, [connected, ambientConnected, eyeConnected, agents]);

  const Tab = TABS[active];

  return (
    <div className="motx-root" style={{ width:"100%", height:"100vh", display:"flex", background:"#050B18", position:"relative", overflow:"hidden" }}>
      <div style={{ position:"absolute", inset:0, overflow:"hidden", pointerEvents:"none", zIndex:0 }}>
        <div style={{ position:"absolute", width:700, height:700, top:-220, right:-120, background:"radial-gradient(circle, rgba(6,182,212,.1) 0%, transparent 65%)", borderRadius:"50%", animation:"blob1 14s ease-in-out infinite" }}/>
        <div style={{ position:"absolute", width:550, height:550, bottom:-180, left:-80, background:"radial-gradient(circle, rgba(124,58,237,.09) 0%, transparent 65%)", borderRadius:"50%", animation:"blob2 17s ease-in-out infinite" }}/>
        <div style={{ position:"absolute", width:420, height:420, top:"35%", left:"42%", background:"radial-gradient(circle, rgba(59,130,246,.05) 0%, transparent 65%)", borderRadius:"50%", animation:"blob3 20s ease-in-out infinite" }}/>
      </div>

      <aside style={{ width:216, height:"100vh", flexShrink:0, display:"flex", flexDirection:"column", padding:"28px 14px", background:"rgba(5,11,24,.75)", borderRight:"1px solid rgba(255,255,255,.06)", backdropFilter:"blur(40px)", boxShadow:"4px 0 48px rgba(0,0,0,.55)", position:"relative", zIndex:20 }}>
        <div style={{ paddingLeft:6, marginBottom:36 }}>
          <div style={{ fontSize:19, fontWeight:600, letterSpacing:"0.04em", color:"#E2E8F0" }}>MOT-X</div>
          <div style={{ fontSize:10, color:"rgba(226,232,240,.25)", letterSpacing:"0.18em", textTransform:"uppercase", marginTop:4 }}>Cognitive OS · v2</div>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:8, padding:"8px 12px", borderRadius:10, marginBottom:28, background: connected ? "rgba(16,185,129,.12)" : "rgba(239,68,68,.07)", border: `1px solid ${connected ? "rgba(16,185,129,.2)" : "rgba(239,68,68,.14)"}` }}>
          {connected ? <Wifi size={12} color="rgba(110,231,183,.85)" strokeWidth={1.5}/> : <WifiOff size={12} color="rgba(252,165,165,.6)" strokeWidth={1.5}/>}
          <span style={{ fontSize:12, color: connected ? "rgba(110,231,183,.9)" : "rgba(252,165,165,.7)", fontWeight:500 }}>{connected ? "Connecté" : "Déconnecté"}</span>
          <div style={{ width:6, height:6, borderRadius:"50%", background: connected ? "#10B981" : "#EF4444", marginLeft:"auto", animation:"pulse 2s ease infinite" }}/>
        </div>
        <nav style={{ display:"flex", flexDirection:"column", gap:3, flex:1 }}>
          {NAV.map(({ id, label, Icon }) => (
            <div key={id} className={`nav-item${active===id?" active":""}`} onClick={() => setActive(id)}>
              <Icon size={15} strokeWidth={1.5}/>{label}
            </div>
          ))}
        </nav>
        <div style={{ padding:"12px 14px", borderRadius:12, background:"rgba(255,255,255,.025)", border:"1px solid rgba(255,255,255,.05)" }}>
          <div style={{ fontSize:10, color:"rgba(226,232,240,.22)", letterSpacing:"0.12em", textTransform:"uppercase", marginBottom:6 }}>Système</div>
          <div style={{ display:"flex", alignItems:"center", gap:6, fontSize:12, color:"rgba(226,232,240,.3)" }}>
            <Database size={11} strokeWidth={1.5}/> ChromaDB · Hors ligne
          </div>
        </div>
      </aside>

      <main style={{ flex:1, overflow:"auto", padding:"36px 38px 36px", position:"relative", zIndex:10 }}>
        <Tab
          ambientUpdate={ambientUpdate}
          eyeGaze={eyeGaze}
          connected={connected}
          ambientConnected={ambientConnected}
          eyeConnected={eyeConnected}
          executionLog={executionLog}
          dashboardMetrics={dashboardMetrics}
          services={services}
          onRunCommand={handleRunCommand}
          agents={agents}
          onToggleAgent={handleToggleAgent}
          run={(target) => { console.log('run ->', target); if (target) setActive(target); }}
        />
      </main>
    </div>
  );
}
