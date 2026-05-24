import { useState } from 'react';
import { API_BASE } from '../lib/apiConfig';

function Cognitive() {
  const [instruction, setInstruction] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!instruction.trim()) return;
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/cognitive`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instruction, user_id: 'web-user' })
      });
      setResult(await response.json());
    } catch (error) {
      setResult({ error: 'Erreur de cycle cognitif' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1>🧠 Cognitif</h1>
      <textarea
        value={instruction}
        onChange={(e) => setInstruction(e.target.value)}
        placeholder="Entrez une instruction cognitive"
        rows={4}
      />
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? '🧠 Chargement...' : 'Analyser'}
      </button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

export default Cognitive;
