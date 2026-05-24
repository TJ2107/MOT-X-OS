import { useEffect, useState } from 'react';
import { API_BASE } from '../lib/apiConfig';
import useStore from '../store/appStore';
import StatCard from '../components/StatCard';
import RecentExecutions from '../components/RecentExecutions';
import SystemStatus from '../components/SystemStatus';
import QuickActions from '../components/QuickActions';

function Dashboard() {
  const { executionHistory, analyticsData } = useStore();
  const [stats, setStats] = useState({
    totalExecutions: 0,
    successRate: 0,
    averageSpeed: 0,
    activeAgents: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/analytics/dashboard`);
        const data = await response.json();
        const analytics = data.analytics || {};
        const successful = executionHistory.filter((e) => e.data?.status === 'success').length;
        setStats({
          totalExecutions: analytics.total_executions ?? executionHistory.length,
          successRate: analytics.success_rate ?? (executionHistory.length > 0 ? ((successful / executionHistory.length) * 100).toFixed(1) : 0),
          averageSpeed: analytics.average_speed_seconds ?? 0,
          activeAgents: analytics.active_agents ?? analytics.active_workflows ?? 0
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
        // fallback to local data
        const successful = executionHistory.filter((e) => e.data?.status === 'success').length;
        setStats({
          totalExecutions: executionHistory.length,
          successRate: executionHistory.length > 0 ? ((successful / executionHistory.length) * 100).toFixed(1) : 0,
          averageSpeed: 0,
          activeAgents: 0
        });
      }
    };

    fetchStats();
  }, [executionHistory, analyticsData]);

  return (
    <div className="dashboard-container">
      <h1>📊 Dashboard</h1>

      <div className="stats-grid">
        <StatCard icon="⚡" label="Total Exécutions" value={stats.totalExecutions} />
        <StatCard icon="✅" label="Taux de Succès" value={`${stats.successRate}%`} />
        <StatCard icon="⏱️" label="Vitesse Moyenne" value={`${stats.averageSpeed.toFixed(2)}s`} />
        <StatCard icon="🤖" label="Agents Actifs" value={stats.activeAgents} />
      </div>

      <div className="dashboard-content">
        <div className="left-panel">
          <QuickActions />
          <SystemStatus />
        </div>
        <div className="right-panel">
          <RecentExecutions executions={executionHistory.slice(0, 5)} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
