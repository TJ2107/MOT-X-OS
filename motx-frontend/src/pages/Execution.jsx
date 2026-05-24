import { useState } from 'react';
import { API_BASE } from '../lib/apiConfig';
import useStore from '../store/appStore';

function Execution() {
  const [instruction, setInstruction] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const addExecution = useStore((state) => state.addExecution);

  const handleExecute = async (e) => {
    e.preventDefault();
    if (!instruction.trim()) return;
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instruction, user_id: useStore.getState().userId })
      });
      const data = await response.json();
      setResult(data);
      addExecution(data);
      setInstruction('');
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Erreur lors de l exécution' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1>⚡ Exécution</h1>
      <form onSubmit={handleExecute} className="execution-form">
        <textarea
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder="Ex: Create folder workspace, Open notepad..."
          rows={5}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? '⏳ Exécution...' : '🚀 Exécuter'}
        </button>
      </form>
      {result && (
        <div className="result-box">
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Execution;
