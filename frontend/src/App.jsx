
import React, { useState } from "react";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Dashboard from "./pages/Dashboard";
import AnalysisResult from "./pages/AnalysisResult";
import AIMemory from "./pages/AIMemory";
import IncidentHistory from "./pages/IncidentHistory";
import VerifyResolution from "./pages/VerifyResolution";
import Settings from "./pages/Settings";

import "./App.css";

export default function App() {
  const [page, setPage] = useState("Dashboard");
  const [incident, setIncident] = useState(null);
  const [history, setHistory] = useState([]);
  const [memory, setMemory] = useState([]);
  const [historyFilter, setHistoryFilter] = useState("All");

  // Simple page navigation
  const navigate = (nextPage, filter = "All") => {
    setPage(nextPage);

    if (nextPage === "Incident History") {
      setHistoryFilter(filter);
    }
  };

  // Analyse logs submitted through the Dashboard chat popup
  const analyse = (inputLogs) => {
    if (!inputLogs || !inputLogs.trim()) {
      alert("Please enter incident logs first.");
      return;
    }

    const submittedLogs = inputLogs.trim();

    const isHigh =
      /fatal|critical|connection refused|timeout|http 500/i.test(
        submittedLogs
      );

    const newId = `INC-${String(Date.now()).slice(-8)}`;

    const result = {
      id: newId,
      summary: isHigh
        ? "High-severity incident detected. The submitted logs indicate a possible service or connectivity failure."
        : "Incident logs received. A potential application issue requires further investigation.",
      severity: isHigh ? "High" : "Medium",
      status: "Open",
      suspected_causes: [
        "Service connectivity or availability issue",
        "Application configuration or deployment problem",
        "Resource constraints or application timeout",
      ],
      evidence: [
        "Error patterns detected in the submitted logs",
        "Potential failure indicators require verification",
      ],
      recommended_checks: [
        "Check application and server health",
        "Review recent deployments and configuration changes",
        "Inspect network connectivity and service dependencies",
        "Compare with similar historical incidents",
      ],
      logs: submittedLogs,
      date: new Date().toLocaleString(),
    };

    setIncident(result);
    setHistory((previous) => [result, ...previous]);
    setPage("Analysis Result");
  };

  // Save verified resolution
  const saveResolution = (rootCause, resolution) => {
    if (!incident) return;

    const updatedIncident = {
      ...incident,
      status: "Resolved",
      confirmed_root_cause: rootCause,
      verified_resolution: resolution,
    };

    setIncident(updatedIncident);

    setHistory((previous) =>
      previous.map((item) =>
        item.id === incident.id ? updatedIncident : item
      )
    );

    setMemory((previous) => [
      {
        id: `MEM-${Date.now()}`,
        incidentId: incident.id,
        rootCause,
        resolution,
        date: new Date().toLocaleString(),
      },
      ...previous,
    ]);

    setPage("AI Memory");
  };

  // Open selected incident
  const viewIncident = (item) => {
    setIncident(item);
    setPage("Analysis Result");
  };

  // Render current page
  const renderPage = () => {
    switch (page) {
      case "Dashboard":
        return (
          <Dashboard
            history={history}
            memory={memory}
            onNavigate={navigate}
            onAnalyseLogs={analyse}
          />
        );

      case "Analysis Result":
        return (
          <AnalysisResult
            incident={incident}
            onVerify={() => setPage("Verify Resolution")}
            onViewMemory={() => setPage("AI Memory")}
          />
        );

      case "Incident History":
        return (
          <IncidentHistory
            history={history}
            onView={viewIncident}
            initialFilter={historyFilter}
          />
        );

      case "AI Memory":
        return <AIMemory memory={memory} />;

      case "Verify Resolution":
        return (
          <VerifyResolution
            incident={incident}
            onSave={saveResolution}
          />
        );

      case "Settings":
        return <Settings />;

      default:
        return (
          <Dashboard
            history={history}
            memory={memory}
            onNavigate={navigate}
            onAnalyseLogs={analyse}
          />
        );
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        activePage={page}
        onNavigate={navigate}
      />

      <div className="main-container">
        <Header page={page} />

        <main className="page-content">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
