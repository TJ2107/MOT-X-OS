import { useEffect, useState } from 'react';
import { API_BASE } from '../lib/apiConfig';

function Agents() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/agents/status`)
      .then((res) => res.json())
      .then(setStatus)
      .catch(() => setStatus({ error: 'Impossible de charger les agents' }));
  }, []);

  return (
    <div className="page-container">
      <h1>🤖 Agents</h1>
      <pre>{JSON.stringify(status, null, 2)}</pre>
    </div>
  );
}

export default Agents;
