function RecentExecutions({ executions }) {
  return (
    <div className="card-section">
      <h3>Exécutions récentes</h3>
      {executions.length === 0 ? (
        <p>Aucune exécution enregistrée.</p>
      ) : (
        <ul>
          {executions.map((execution, index) => (
            <li key={index}>
              <strong>{execution.execution_id || `#${index + 1}`}</strong>
              <pre>{JSON.stringify(execution.data, null, 2)}</pre>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default RecentExecutions;
