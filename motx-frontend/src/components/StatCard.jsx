function StatCard({ icon, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-card-icon">{icon}</div>
      <div className="stat-card-info">
        <span className="stat-card-label">{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

export default StatCard;
