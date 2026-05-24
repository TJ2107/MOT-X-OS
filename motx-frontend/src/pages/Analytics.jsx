import { useEffect, useState } from 'react';
import { API_BASE } from '../lib/apiConfig';

function Analytics() {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/analytics/dashboard`)
      .then((res) => res.json())
      .then(setAnalytics)
      .catch(() => setAnalytics({ error: 'Impossible de charger les analytiques' }));
  }, []);

  return (
    <div className="page-container">
      <h1>📊 Analytiques</h1>
      <pre>{JSON.stringify(analytics, null, 2)}</pre>
    </div>
  );
}

export default Analytics;
