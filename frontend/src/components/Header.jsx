
import React from "react";
import { Bot, CheckCircle2 } from "lucide-react";

const pageDescriptions = {
  Dashboard: "Overview of incidents, system health and AI memory",
  "Analysis Result": "Review incident analysis and recommendations",
  "Incident History": "Browse previously analysed incidents",
  "AI Memory": "Explore historical incidents and verified resolutions",
  "Verify Resolution": "Confirm the root cause and verified fix",
  Settings: "Manage application preferences",
};

export default function Header({ page }) {
  return (
    <header className="top-header">
      <div className="header-brand">
        <Bot size={27} />

        <div>
          <h1>AI Incident Response Agent</h1>
          <p>
            {pageDescriptions[page] || "IncidentAI workspace"}
          </p>
        </div>
      </div>

      <div className="header-status">
        <CheckCircle2 size={15} />
        <span>System Online</span>
      </div>
    </header>
  );
}
