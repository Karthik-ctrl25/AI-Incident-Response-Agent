
import React from "react";
import {
  Bot,
  LayoutDashboard,
  Clock,
  BrainCircuit,
  Settings,
} from "lucide-react";

const navigationItems = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Incident History", icon: Clock },
  { label: "AI Memory", icon: BrainCircuit },
  { label: "Settings", icon: Settings },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <Bot size={27} />
        <span>IR Agent</span>
      </div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.label;

          return (
            <button
              key={item.label}
              type="button"
              className={`sidebar-link ${isActive ? "active" : ""}`}
              onClick={() => onNavigate(item.label)}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon size={19} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <span className="connection-dot" />
        <span>Hindsight Connected</span>
      </div>
    </aside>
  );
}
