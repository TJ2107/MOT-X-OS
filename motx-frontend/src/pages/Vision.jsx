import { useState } from 'react';
import { API_BASE } from '../lib/apiConfig';

function Vision() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    const form = new FormData();
    form.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/api/vision/ocr`, {
        method: 'POST',
        body: form
      });
      setResult(await response.json());
    } catch (error) {
      setResult({ error: 'Erreur OCR' });
    }
  };

  return (
    <div className="page-container">
      <h1>🖼️ Vision</h1>
      <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleUpload}>Envoyer image</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

export default Vision;
