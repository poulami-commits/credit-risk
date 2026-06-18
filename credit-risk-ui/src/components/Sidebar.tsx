import { NavLink } from "react-router-dom";

const links = [
  { to: "/",           icon: "⬡",  label: "Dashboard",   badge: null },
  { to: "/assessment", icon: "◎",  label: "Assessment",  badge: "New" },
  { to: "/health",     icon: "♡",  label: "Health",      badge: null },
  { to: "/model-info", icon: "◈",  label: "Model Info",  badge: null },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">⬡</div>
        <div className="sidebar-brand-text">
          <span className="sidebar-brand-name">CreditRisk AI</span>
          <span className="sidebar-brand-sub">Analytics Platform</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Main</div>
        {links.map(({ to, icon, label, badge }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `sidebar-link${isActive ? " active" : ""}`
            }
          >
            <span className="sidebar-link-icon">{icon}</span>
            {label}
            {badge && (
              <span className="sidebar-link-badge">{badge}</span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-footer-avatar">AR</div>
        <div className="sidebar-footer-info">
          <span className="sidebar-footer-name">Analyst</span>
          <span className="sidebar-footer-role">Risk Officer</span>
        </div>
      </div>
    </aside>
  );
}
