import { useState, useEffect, useRef, useCallback } from "react";
import {
  Activity, Zap, Cpu, Bot, BarChart2, Eye, Database,
  Mic, Scan, RotateCcw
} from "lucide-react";
import { API_BASE, WS_BASE } from "./lib/apiConfig";

// Import modular pages and components
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Execution from "./pages/Execution";
import Cognitive from "./pages/Cognitive";
import Agents from "./pages/Agents";
import Analytics from "./pages/Analytics";
import Vision from "./pages/Vision";
import Onboarding from "./pages/Onboarding";
import { ToastContainer } from "./components/Toast";

const USER_ID_KEY = "motx-user-id";
const initialUserId = () => {
  if (typeof window === "undefined") return "web-user";
  const stored = window.localStorage.getItem(USER_ID_KEY);
  if (stored) return stored;
  const generated = `web-user-${Date.now()}`;
  window.localStorage.setItem(USER_ID_KEY, generated);
  return generated;
};

const NAV = [
  { id: "dashboard",   label: "Dashboard",   Icon: Activity  },
  { id: "execution",   label: "Exécution",   Icon: Zap       },
  { id: "cognitif",    label: "Cognitif",    Icon: Cpu       },
  { id: "agents",      label: "Agents",      Icon: Bot       },
  { id: "analytiques", label: "Analytiques", Icon: BarChart2 },
  { id: "vision",      label: "Vision",      Icon: Eye       },
];

const SERVICES = [
  { label: "FastAPI",     color: "#EF4444", status: "Hors ligne" },
  { label: "ChromaDB",    color: "#EF4444", status: "Hors ligne" },
  { label: "Ollama",      color: "#EF4444", status: "Hors ligne" },
  { label: "Shadow Mode", color: "#6B7280", status: "Inactif"    },
  { label: "Ambient Stream", color: "#6B7280", status: "Inactif" },
  { label: "Eye Tracking",color: "#6B7280", status: "Inactif"    },
  { label: "Voice Engine",color: "#6B7280", status: "Inactif"    },
];

const AGENTS_INIT = [
  { id: "blackhole", name: "Black Hole",       desc: "Ingestion & vectorisation de fichiers", Icon: Database,   color: "#60A5FA", stat: "0 fichiers",    score: 0, active: false },
  { id: "shadow",    name: "Shadow Mode",      desc: "Observation silencieuse & workflows",   Icon: Eye,        color: "#A78BFA", stat: "0 captures",    score: 0, active: false },
  { id: "voice",     name: "Voice Engine",     desc: "Whisper + fallback Google Speech",      Icon: Mic,        color: "#34D399", stat: "0 commandes",   score: 0, active: false },
  { id: "eyetrack",  name: "Eye Tracking",     desc: "MediaPipe · Look & Do interface",       Icon: Scan,       color: "#F472B6", stat: "Non calibré",   score: 0, active: false },
  { id: "rewind",    name: "Semantic Rewind",  desc: "Mémoire épisodique temporelle",         Icon: RotateCcw,  color: "#FBBF24", stat: "0 épisodes",    score: 0, active: false },
];

// Dictionnaire des onglets
const TABS = {
  dashboard: Dashboard,
  execution: Execution,
  cognitif: Cognitive,
  agents: Agents,
  analytiques: Analytics,
  vision: Vision
};

const mergeUiAgents = (remoteAgents) => {
  if (!Array.isArray(remoteAgents)) return AGENTS_INIT;
  return AGENTS_INIT.map((template) => {
    const remote = remoteAgents.find((item) => item.id === template.id);
    if (!remote) return template;
    return {
      ...template,
      active: Boolean(remote.active),
      stat: remote.stat ?? template.stat,
      score: typeof remote.score === "number" ? remote.score : template.score,
    };
  });
};

export default function App() {
  const [active, setActive] = useState("dashboard");
  const [showOnboarding, setShowOnboarding] = useState(() => {
    if (typeof window === "undefined") return false;
    const stored = window.localStorage.getItem("motx-onboarding-done");
    return !stored;
  });
  const [connected, setConnected] = useState(false);
  const [ambientConnected, setAmbientConnected] = useState(false);
  const [eyeConnected, setEyeConnected] = useState(false);
  const [ambientUpdate, setAmbientUpdate] = useState(null);
  const [eyeGaze, setEyeGaze] = useState(null);
  const [executionLog, setExecutionLog] = useState([]);
  const [agents, setAgents] = useState(AGENTS_INIT);
  const [services, setServices] = useState(SERVICES);
  const [dashboardMetrics, setDashboardMetrics] = useState({
    totalExecutions: 0,
    successRate: 0,
    averageSpeed: 0,
    activeAgents: 0,
    discoveredWorkflows: [
      {
        id: "seed_git_commit",
        name: "Git Commit Flow",
        description: "Détecte la séquence : VSCode → Git → Terminal commit",
        confidence: 0.92,
        timestamp: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: "seed_documentation",
        name: "Documentation Update",
        description: "Pattern : Édition fichier → Git add → Git push",
        confidence: 0.87,
        timestamp: new Date(Date.now() - 1800000).toISOString(),
      },
      {
        id: "seed_code_review",
        name: "Code Review Routine",
        description: "Cycle : GitHub PR → VSCode → Terminal tests",
        confidence: 0.78,
        timestamp: new Date(Date.now() - 900000).toISOString(),
      },
    ]
  });
  const [toasts, setToasts] = useState([]);
  const [userId] = useState(initialUserId);
  const genericSocketRef = useRef(null);

  // Fetch History from API
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/history?limit=20&user_id=${encodeURIComponent(userId)}`);
        if (!response.ok) throw new Error(`Backend non accessible (${response.status})`);
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

  // Sync Agents
  useEffect(() => {
    let mounted = true;
    const syncAgents = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/agents/ui`);
        if (!response.ok) return;
        const payload = await response.json();
        if (!mounted) return;
        setAgents(mergeUiAgents(payload.agents));
      } catch (error) {
        console.warn("Impossible de synchroniser les agents UI", error);
      }
    };
    syncAgents();
    const interval = setInterval(syncAgents, 5000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  const applyExecutionResult = useCallback((command, success, message, requestId = null, meta = {}) => {
    const out = typeof message === 'string' ? message : JSON.stringify(message ?? {}, null, 2);
    const effect = meta.effect ?? null;
    const status = effect === 'nexus_recover'
      ? 'warn'
      : (effect === 'nexus_recover_denied' ? 'error' : (success ? 'ok' : 'error'));
    setExecutionLog((prev) => {
      const pendingIndex = prev.findIndex((e) =>
        e.status === 'pending' && (requestId != null ? String(e.id) === String(requestId) : e.cmd === command)
      );
      if (pendingIndex >= 0) {
        return prev.map((e, index) => index === pendingIndex
          ? { ...e, status, out, effect }
          : e
        );
      }
      return [{
        id: Date.now(),
        cmd: command,
        status,
        effect,
        time: new Date().toLocaleTimeString('fr', { hour12: false }),
        out,
        createdAt: new Date().toISOString()
      }, ...prev].slice(0, 50);
    });
  }, []);

  const handleRunCommand = useCallback(async (command) => {
    const requestId = Date.now();
    const isNexusRecover = /^nexus\.recover\s*\(/i.test(command.trim());
    const entry = {
      id: requestId,
      cmd: command,
      status: 'pending',
      time: new Date().toLocaleTimeString('fr', { hour12: false }),
      out: isNexusRecover
        ? '⛔ Nexus sous tension gravitationnelle…\n   Extraction DÉCONSEILLÉE — ne fermez pas cette fenêtre.'
        : 'En cours…',
      createdAt: new Date().toISOString(),
      effect: isNexusRecover ? 'nexus_recover_pending' : null,
    };
    setExecutionLog((prev) => [...prev, entry]);

    const controller = new AbortController();
    const timeoutMs = isNexusRecover ? 60000 : 120000;
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(`${API_BASE}/api/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, user_id: userId }),
        signal: controller.signal,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.detail || payload?.message || `Erreur HTTP ${response.status}`);
      }
      applyExecutionResult(
        command,
        payload.success !== false,
        payload.message,
        requestId,
        { effect: payload.data?.effect }
      );
    } catch (error) {
      const msg = error.name === 'AbortError'
        ? (isNexusRecover 
            ? `Délai dépassé (${timeoutMs / 1000}s). Le Nexus a peut‑être refusé l'extraction.` 
            : `Délai dépassé (${timeoutMs / 1000}s). Le traitement IA prend plus de temps que prévu.`)
        : (error.message || 'Erreur lors de l\'exécution');
      applyExecutionResult(command, false, msg, requestId, {
        effect: isNexusRecover ? 'nexus_recover_denied' : null,
      });
    } finally {
      clearTimeout(timeoutId);
    }
  }, [userId, applyExecutionResult]);

  // WebSocket subscriptions
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
          if (payload?.type === 'execution_result') {
            const message = payload.message
              ?? (payload.data ? JSON.stringify(payload.data, null, 2) : null)
              ?? (payload.success ? 'Résultat reçu' : 'Erreur du service');
            applyExecutionResult(
              payload.command || 'unknown',
              payload.success !== false,
              message,
              payload.request_id ?? null,
              { effect: payload.data?.effect }
            );
          }
          if (payload?.type === 'agent_update' && payload.agent_id) {
            setAgents((prev) => prev.map((agent) =>
              agent.id === payload.agent_id
                ? {
                  ...agent,
                  active: payload.active ?? agent.active,
                  stat: payload.stat ?? agent.stat,
                  score: typeof payload.score === 'number' ? payload.score : agent.score,
                }
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
  }, [userId, applyExecutionResult]);

  // Fetch Dashboard Metrics
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
        const discoveredWorkflows = payload.discoveredWorkflows || [];

        setDashboardMetrics({
          totalExecutions,
          successRate,
          averageSpeed,
          activeAgents,
          discoveredWorkflows
        });
      } catch (error) {
        console.warn('Impossible de charger les métriques du dashboard', error);
        const successful = executionLog.filter((e) => e.status === 'ok').length;
        setDashboardMetrics((prev) => ({
          totalExecutions: executionLog.length,
          successRate: executionLog.length ? (successful / executionLog.length) * 100 : 0,
          averageSpeed: 0,
          activeAgents: agents.filter((agent) => agent.active).length,
          discoveredWorkflows: prev.discoveredWorkflows || []
        }));
      }
    };
    fetchDashboardMetrics();
  }, [executionLog, agents, connected]);

  // Periodically Poll /api/status for ChromaDB status
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

  const handleToggleAgent = async (agentId) => {
    const current = agents.find((agent) => agent.id === agentId);
    if (!current) return;
    const nextActive = !current.active;
    setAgents((prev) => prev.map((agent) =>
      agent.id === agentId ? { ...agent, active: nextActive } : agent
    ));
    try {
      const response = await fetch(`${API_BASE}/api/agents/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: agentId, active: nextActive }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload?.detail || `Erreur HTTP ${response.status}`);
      if (payload.agents) {
        setAgents(mergeUiAgents(payload.agents));
      }
    } catch (error) {
      console.warn("Échec activation agent", error);
      setAgents((prev) => prev.map((agent) =>
        agent.id === agentId ? { ...agent, active: !nextActive } : agent
      ));
    }
  };

  const handleCompleteOnboarding = () => {
    setShowOnboarding(false);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("motx-onboarding-done", "true");
    }
  };

  const addToast = useCallback((type = "info", title = "", message = "", duration = 4000) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    setToasts((prev) => [...prev, { id, type, title, message, duration }]);
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  // Emit toast when Shadow Mode detects activity
  useEffect(() => {
    const shadowAgent = agents.find((a) => a.id === "shadow");
    if (shadowAgent?.active) {
      // Simulate detection events
      const interval = setInterval(() => {
        if (Math.random() > 0.6) {
          const messages = [
            { title: "🕵️ Activité détectée", message: "Pattern VSCode → Terminal observé" },
            { title: "🔄 Pattern reconnu", message: "Git workflow en cours d'exécution" },
            { title: "🎯 Workflow découvert", message: "Nouvelle routine d'automation détectée" },
            { title: "✨ Suggestion", message: "Vous pourriez automatiser cette séquence" },
          ];
          const msg = messages[Math.floor(Math.random() * messages.length)];
          addToast("shadow", msg.title, msg.message, 5000);
        }
      }, 4000);

      return () => clearInterval(interval);
    }
  }, [agents, addToast]);

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

  const TabComponent = TABS[active];

  return (
    <>
      {showOnboarding && <Onboarding onComplete={handleCompleteOnboarding} />}
      
      <div className="motx-root" style={{ width: "100%", height: "100vh", display: "flex", background: "#050B18", position: "relative", overflow: "hidden" }}>
      {/* Background Animated Blobs */}
      <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none", zIndex: 0 }}>
        <div style={{ position: "absolute", width: 700, height: 700, top: -220, right: -120, background: "radial-gradient(circle, rgba(6,182,212,.08) 0%, transparent 65%)", borderRadius: "50%", animation: "blob1 14s ease-in-out infinite" }}/>
        <div style={{ position: "absolute", width: 550, height: 550, bottom: -180, left: -80, background: "radial-gradient(circle, rgba(124,58,237,.07) 0%, transparent 65%)", borderRadius: "50%", animation: "blob2 17s ease-in-out infinite" }}/>
        <div style={{ position: "absolute", width: 420, height: 420, top: "35%", left: "42%", background: "radial-gradient(circle, rgba(59,130,246,.04) 0%, transparent 65%)", borderRadius: "50%", animation: "blob3 20s ease-in-out infinite" }}/>
      </div>

      <Sidebar
        active={active}
        setActive={setActive}
        connected={connected}
        services={services}
        navItems={NAV}
      />

      <main style={{ flex: 1, overflow: "auto", padding: "36px 38px 36px", position: "relative", zIndex: 10 }}>
        <TabComponent
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
          run={(target) => { if (target) setActive(target); }}
        />
      </main>
      </div>

      <ToastContainer toasts={toasts} onClose={removeToast} />
    </>
  );
}
