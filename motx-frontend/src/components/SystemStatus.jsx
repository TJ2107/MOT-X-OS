import { useEffect, useState } from 'react';
import { API_BASE } from '../lib/apiConfig';

function SystemStatus() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/status`)
      .then((res) => res.json())
      .then(setStatus)
      .catch(() => setStatus({ error: 'Unable to fetch status' }));
  }, []);

  return (
    <div className="card-section">
      <h3>Statut du système</h3>
      <pre>{JSON.stringify(status, null, 2)}</pre>
    </div>
  );
}

export default SystemStatus;
