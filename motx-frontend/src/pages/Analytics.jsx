import { Zap, CheckCircle, Clock } from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";

const SLabel = ({ children }) => (
  <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 16 }}>
    {children}
  </div>
);

const WEEKDAY_LABELS = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"];

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

const ChartTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "rgba(8,13,26,.95)", border: "1px solid rgba(255,255,255,.1)", borderRadius: 10, padding: "10px 14px", backdropFilter: "blur(20px)" }}>
      <p style={{ fontSize: 11, color: "rgba(226,232,240,.4)", marginBottom: 6 }}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ fontSize: 13, color: p.color, fontWeight: 500 }}>{p.name} : {p.value}</p>
      ))}
    </div>
  );
};

function Analytics({ executionLog, agents, ambientUpdate, eyeGaze, services, connected, ambientConnected, eyeConnected }) {
  const weekData = buildWeekAnalytics(executionLog, agents);
  const total = executionLog.length;
  const successRate = total ? Math.round(executionLog.filter((e) => e.status === 'ok').length / total * 100) : 0;
  const allLatencies = executionLog.map((entry) => {
    const match = entry.out?.match(/(\d+(?:[.,]\d+)?)\s*ms/);
    return match ? Number(match[1].replace(",", ".")) : null;
  }).filter((value) => value != null);
  const avgLatency = allLatencies.length ? (allLatencies.reduce((s, v) => s + v, 0) / allLatencies.length).toFixed(2) : '—';
  const activeAgents = agents.filter((agent) => agent.active).length;
  const cognitiveState = ambientUpdate?.cognitive_state ?? 'Inconnu';
  const gazePosition = eyeGaze ? `x:${Math.round(eyeGaze.x)} y:${Math.round(eyeGaze.y)}` : 'Aucun';
  const fastApiStatus = connected ? 'En ligne' : 'Hors ligne';
  const ollamaStatus = services.find((s) => s.label === 'Ollama')?.status ?? 'Inconnu';
  const chromaStatus = services.find((s) => s.label === 'ChromaDB')?.status ?? 'Inconnu';

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ animation: "fadeUp .35s ease both" }}>
        <div style={{ fontSize: 10, color: "rgba(226,232,240,.28)", letterSpacing: "0.16em", textTransform: "uppercase", marginBottom: 8 }}>7 derniers jours</div>
        <h1 style={{ fontSize: 28, fontWeight: 600, color: "#E2E8F0", letterSpacing: "-0.02em" }}>Analytiques</h1>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
        {[
          { label: "Exécutions totales", value: total,          color: "#60A5FA", Icon: Zap,         sub: "cette semaine" },
          { label: "Taux de succès",     value: `${successRate}%`, color: "#10B981", Icon: CheckCircle, sub: "en moyenne" },
          { label: "Latence moyenne",    value: `${avgLatency}s`,  color: "#F59E0B", Icon: Clock,       sub: "par requête" },
        ].map(({ label, value, color, Icon }) => (
          <div key={label} className="glass" style={{ padding: "20px 22px", display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ width: 40, height: 40, borderRadius: 11, background: `${color}18`, border: `1px solid ${color}28`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <Icon size={16} color={color} strokeWidth={1.5} />
            </div>
            <div>
              <div style={{ fontSize: 22, fontWeight: 600, color: "#E2E8F0", fontFamily: "'JetBrains Mono',monospace", letterSpacing: "-0.02em" }}>{value}</div>
              <div style={{ fontSize: 11, color: "rgba(226,232,240,.35)", marginTop: 2 }}>{label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="glass" style={{ padding: "22px 22px 14px" }}>
        <SLabel>Exécutions · 7 jours</SLabel>
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={weekData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
            <defs>
              <linearGradient id="gExec" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#60A5FA" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#60A5FA" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gSucc" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false} />
            <XAxis dataKey="day" tick={{ fill: "rgba(226,232,240,.3)", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "rgba(226,232,240,.3)", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip content={<ChartTip />} />
            <Area type="monotone" dataKey="execs"   name="Exécutions" stroke="#60A5FA" strokeWidth={2} fill="url(#gExec)" dot={false} />
            <Area type="monotone" dataKey="success" name="Succès"      stroke="#10B981" strokeWidth={2} fill="url(#gSucc)" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div className="glass" style={{ padding: "22px 22px 14px" }}>
          <SLabel>Latence (s)</SLabel>
          <ResponsiveContainer width="100%" height={120}>
            <AreaChart data={weekData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="gLat" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false} />
              <XAxis dataKey="day" tick={{ fill: "rgba(226,232,240,.3)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "rgba(226,232,240,.3)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTip />} />
              <Area type="monotone" dataKey="latency" name="Latence" stroke="#F59E0B" strokeWidth={2} fill="url(#gLat)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="glass" style={{ padding: "22px 22px 14px" }}>
          <SLabel>Agents actifs / jour</SLabel>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={weekData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.04)" vertical={false} />
              <XAxis dataKey="day" tick={{ fill: "rgba(226,232,240,.3)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "rgba(226,232,240,.3)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTip />} />
              <Bar dataKey="agents" name="Agents" fill="#A78BFA" radius={[4, 4, 0, 0]} fillOpacity={0.75} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="glass" style={{ padding: "22px 22px 14px" }}>
        <SLabel>Statut live</SLabel>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          {[
            { label: 'FastAPI', value: fastApiStatus, color: connected ? '#10B981' : '#EF4444' },
            { label: 'ChromaDB', value: chromaStatus, color: chromaStatus === 'En ligne' ? '#10B981' : '#EF4444' },
            { label: 'Ollama', value: ollamaStatus, color: ollamaStatus === 'En ligne' ? '#10B981' : '#EF4444' },
            { label: 'Ambient', value: ambientConnected ? 'Actif' : 'Inactif', color: ambientConnected ? '#10B981' : '#6B7280' },
            { label: 'Eye Tracking', value: eyeConnected ? 'Actif' : 'Inactif', color: eyeConnected ? '#10B981' : '#6B7280' },
            { label: 'Agents actifs', value: `${activeAgents}`, color: activeAgents ? '#10B981' : '#6B7280' }
          ].map(({ label, value, color }) => (
            <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: 12, borderRadius: 12, background: 'rgba(255,255,255,.03)', border: '1px solid rgba(255,255,255,.05)' }}>
              <span style={{ fontSize: 10, color: 'rgba(226,232,240,.4)', textTransform: 'uppercase' }}>{label}</span>
              <span style={{ fontSize: 15, color, fontWeight: 600 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="glass" style={{ padding: "22px 22px 14px" }}>
        <SLabel>Statut de l'environnement</SLabel>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div style={{ padding: 12, borderRadius: 12, background: 'rgba(255,255,255,.03)', border: '1px solid rgba(255,255,255,.05)' }}>
            <div style={{ fontSize: 12, color: 'rgba(226,232,240,.4)', marginBottom: 6 }}>État cognitif</div>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#93C5FD' }}>{cognitiveState}</div>
          </div>
          <div style={{ padding: 12, borderRadius: 12, background: 'rgba(255,255,255,.03)', border: '1px solid rgba(255,255,255,.05)' }}>
            <div style={{ fontSize: 12, color: 'rgba(226,232,240,.4)', marginBottom: 6 }}>Position regard</div>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#60A5FA' }}>{gazePosition}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
