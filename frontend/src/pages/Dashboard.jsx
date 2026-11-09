
import React, { useState } from "react";

import {
  Database,
  AlertTriangle,
  CheckCircle2,
  BrainCircuit,
  Activity,
  Clock,
  Bot,
  Send,
  MessageCircle,
  X,
  Sparkles,
} from "lucide-react";

export default function Dashboard({
  history = [],
  memory = [],
  onNavigate,
  onAnalyseLogs,
  isAnalyzing = false,
  analysisError = "",
}) {
  const [chatOpen, setChatOpen] = useState(false);
  const [message, setMessage] = useState("");

  const totalIncidents = history.length;

  const criticalIncidents = history.filter(
    (item) =>
      item.severity === "High" ||
      item.severity === "Critical"
  ).length;

  const resolvedIncidents = history.filter(
    (item) => item.status === "Resolved"
  ).length;

  const highCount = criticalIncidents;

  const mediumCount = history.filter(
    (item) => item.severity === "Medium"
  ).length;

  const lowCount = history.filter(
    (item) => item.severity === "Low"
  ).length;

  const totalForChart = Math.max(history.length, 1);

  const highPercent = (highCount / totalForChart) * 100;
  const mediumPercent = (mediumCount / totalForChart) * 100;

  const severityBackground =
    history.length === 0
      ? "#303b32"
      : `conic-gradient(
          #d97770 0% ${highPercent}%,
          #d6a05f ${highPercent}% ${highPercent + mediumPercent}%,
          #3c966b ${highPercent + mediumPercent}% 100%
        )`;

  // Submit logs to the backend through App.jsx
  const sendMessage = () => {
    if (!message.trim() || isAnalyzing) return;

    const submittedMessage = message.trim();

    setMessage("");

    // Keep chat open while the backend processes the logs.
    onAnalyseLogs?.(submittedMessage);
  };

  const recentActivity = history.slice(0, 5);

  return (
    <div className="dashboard-page">

      {/* DASHBOARD HEADING */}
      <div className="page-heading dashboard-heading">
        <div>
          <h2>Dashboard</h2>
          <p>
            Overview of incidents, system health and AI memory
          </p>
        </div>

        <div className="memory-status">
          <span className="connection-dot" />
          Hindsight Memory: Ready
        </div>
      </div>

      {/* STATISTICS CARDS */}
      <div className="statistics-grid">

        <button
          type="button"
          className="metric-card clickable-card"
          onClick={() => onNavigate?.("Incident History", "All")}
        >
          <div className="metric-icon green">
            <Database size={22} />
          </div>

          <div className="metric-content">
            <h3>{totalIncidents}</h3>
            <p>Total Incidents</p>
            <small>Click to view details</small>
          </div>
        </button>

        <button
          type="button"
          className="metric-card clickable-card"
          onClick={() => onNavigate?.("Incident History", "Critical")}
        >
          <div className="metric-icon red">
            <AlertTriangle size={22} />
          </div>

          <div className="metric-content">
            <h3>{criticalIncidents}</h3>
            <p>Critical / High</p>
            <small>Click to view details</small>
          </div>
        </button>

        <button
          type="button"
          className="metric-card clickable-card"
          onClick={() => onNavigate?.("Incident History", "Resolved")}
        >
          <div className="metric-icon emerald">
            <CheckCircle2 size={22} />
          </div>

          <div className="metric-content">
            <h3>{resolvedIncidents}</h3>
            <p>Resolved</p>
            <small>Click to view details</small>
          </div>
        </button>

        <button
          type="button"
          className="metric-card clickable-card"
          onClick={() => onNavigate?.("AI Memory")}
        >
          <div className="metric-icon gold">
            <BrainCircuit size={22} />
          </div>

          <div className="metric-content">
            <h3>{memory.length}</h3>
            <p>Historical Memories</p>
            <small>Click to view details</small>
          </div>
        </button>

      </div>

      {/* DASHBOARD PANELS */}
      <div className="dashboard-bottom">

        {/* SEVERITY DISTRIBUTION */}
        <section className="content-panel">
          <div className="section-heading">
            <div>
              <h3>Incident Severity Distribution</h3>
              <p>Breakdown of analysed incidents</p>
            </div>

            <Activity size={20} />
          </div>

          {history.length === 0 ? (
            <div className="empty-state">
              <Activity size={27} />
              <p>No incidents analysed yet.</p>
              <span>
                Open IncidentAI chat to submit server logs.
              </span>
            </div>
          ) : (
            <div className="severity-layout">
              <div
                className="severity-donut"
                style={{ background: severityBackground }}
              >
                <div className="donut-center">
                  <strong>{history.length}</strong>
                  <span>Incidents</span>
                </div>
              </div>

              <div className="severity-details">
                <div className="severity-item">
                  <span className="severity-dot critical" />
                  High / Critical
                  <b>{highCount}</b>
                </div>

                <div className="severity-item">
                  <span className="severity-dot medium" />
                  Medium
                  <b>{mediumCount}</b>
                </div>

                <div className="severity-item">
                  <span className="severity-dot low" />
                  Low
                  <b>{lowCount}</b>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* RECENT ACTIVITY */}
        <section className="content-panel">
          <div className="section-heading">
            <div>
              <h3>Recent AI Activity</h3>
              <p>Latest incident intelligence</p>
            </div>

            <Activity size={20} />
          </div>

          {recentActivity.length === 0 ? (
            <div className="empty-state">
              <BrainCircuit size={27} />
              <p>No recent activity</p>
              <span>
                Analysed incidents will appear here.
              </span>
            </div>
          ) : (
            <div className="activity-list">
              {recentActivity.map((item) => (
                <button
                  type="button"
                  className="activity-item dashboard-activity-button"
                  key={item.id}
                  onClick={() => onNavigate?.("Incident History", "All")}
                >
                  <div className="activity-symbol">
                    <BrainCircuit size={16} />
                  </div>

                  <div className="activity-title">
                    <strong>{item.id}</strong>
                    <div>{item.summary}</div>
                  </div>

                  <div className="activity-time">
                    <Clock size={12} />
                    {item.severity}
                  </div>
                </button>
              ))}
            </div>
          )}

          <button
            type="button"
            className="dashboard-history-link"
            onClick={() => onNavigate?.("Incident History", "All")}
          >
            View incident history
          </button>
        </section>

      </div>

      {/* FLOATING INCIDENT AI CHAT */}
      <div className="incident-chat-widget">

        {chatOpen && (
          <section
            className="incident-chat-window"
            aria-label="IncidentAI assistant"
          >

            {/* CHAT HEADER */}
            <div className="incident-chat-header">
              <div className="incident-chat-profile">
                <div className="incident-chat-avatar">
                  <Bot size={23} />
                </div>

                <div>
                  <h3>IncidentAI Assistant</h3>
                  <span>
                    <i />
                    {isAnalyzing
                      ? "Analysing incident..."
                      : "Available to help"}
                  </span>
                </div>
              </div>

              <button
                type="button"
                className="incident-chat-close"
                onClick={() => setChatOpen(false)}
                aria-label="Close chat"
              >
                <X size={19} />
              </button>
            </div>

            {/* CHAT BODY */}
            <div className="incident-chat-body">

              <div className="chat-date-label">
                IncidentAI Support
              </div>

              <div className="chat-message assistant-message">
                <div className="chat-message-icon">
                  <Bot size={16} />
                </div>

                <div className="chat-bubble">
                  <strong>
                    Hello! I'm IncidentAI.
                  </strong>

                  <p>
                    I can help you investigate application
                    incidents, understand server errors and
                    identify possible root causes.
                  </p>

                  <span>
                    How can I help you today?
                  </span>
                </div>
              </div>

              <div className="chat-hint">
                <Sparkles size={15} />
                <span>
                  Describe your issue or paste your server logs
                  to begin an investigation.
                </span>
              </div>

              {/* LOADING MESSAGE */}
              {isAnalyzing && (
                <div className="chat-hint">
                  <Sparkles size={15} />
                  <span>
                    IncidentAI is analysing your logs.
                    Please wait...
                  </span>
                </div>
              )}

              {/* BACKEND ERROR MESSAGE */}
              {analysisError && (
                <div className="chat-hint" role="alert">
                  <AlertTriangle size={15} />
                  <span>{analysisError}</span>
                </div>
              )}

            </div>

            {/* CHAT INPUT */}
            <div className="incident-chat-compose">

              <textarea
                value={message}
                onChange={(event) =>
                  setMessage(event.target.value)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Type a message or paste server logs..."
                rows={3}
                aria-label="Message IncidentAI"
                disabled={isAnalyzing}
              />

              <div className="incident-chat-compose-footer">
                <span>
                  Shift + Enter for a new line
                </span>

                <button
                  type="button"
                  className="chat-analyse-button"
                  onClick={sendMessage}
                  disabled={!message.trim() || isAnalyzing}
                >
                  {isAnalyzing ? (
                    "Analysing..."
                  ) : (
                    <>
                      <Send size={15} />
                      Send
                    </>
                  )}
                </button>
              </div>

            </div>

            {/* CHAT FOOTER */}
            <div className="incident-chat-footer">
              <span>
                <Sparkles size={12} />
                AI-powered incident assistance
              </span>
            </div>

          </section>
        )}

        {/* FLOATING CHAT LAUNCHER */}
        <button
          type="button"
          className={`incident-chat-launcher ${
            chatOpen ? "chat-launcher-open" : ""
          }`}
          onClick={() =>
            setChatOpen((previous) => !previous)
          }
          aria-label={
            chatOpen
              ? "Close IncidentAI chat"
              : "Open IncidentAI chat"
          }
        >
          {chatOpen ? (
            <X size={23} />
          ) : (
            <>
              <MessageCircle size={23} />
              <span className="chat-launcher-label">
                Ask IncidentAI
              </span>
            </>
          )}
        </button>

      </div>
    </div>
  );
}
