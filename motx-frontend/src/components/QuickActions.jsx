function QuickActions() {
  return (
    <div className="card-section">
      <h3>Actions rapides</h3>
      <button onClick={() => window.location.assign('/execution')}>Lancer une exécution</button>
      <button onClick={() => window.location.assign('/analytics')}>Voir analytiques</button>
      <button onClick={() => window.location.assign('/agents')}>Vérifier agents</button>
    </div>
  );
}

export default QuickActions;
