import { NavLink } from 'react-router-dom';

function Sidebar({ connected }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>MOT-X v2</h1>
        <span className={connected ? 'status active' : 'status inactive'}>
          {connected ? 'Connecté' : 'Déconnecté'}
        </span>
      </div>
      <nav>
        <NavLink to="/">Dashboard</NavLink>
        <NavLink to="/execution">Exécution</NavLink>
        <NavLink to="/cognitive">Cognitif</NavLink>
        <NavLink to="/agents">Agents</NavLink>
        <NavLink to="/analytics">Analytiques</NavLink>
        <NavLink to="/vision">Vision</NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;
