
import React, { useState } from "react";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Dashboard from "./pages/Dashboard";
import AnalysisResult from "./pages/AnalysisResult";
import AIMemory from "./pages/AIMemory";
import IncidentHistory from "./pages/IncidentHistory";
import VerifyResolution from "./pages/VerifyResolution";
import Settings from "./pages/Settings";

import {
  analyzeIncident,
  verifyIncident,
  getIncidentDetails,
} from "./services/api";

import "./App.css";

export default function App() {
  const [page, setPage] = useState("Dashboard");
  const [incident, setIncident] = useState(null);
  const [history, setHistory] = useState([]);
  const [memory, setMemory] = useState([]);
  const [historyFilter, setHistoryFilter] = useState("All");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [verificationError, setVerificationError] = useState("");

  const [isFetchingIncident, setIsFetchingIncident] = useState(false);
  const [incidentFetchError, setIncidentFetchError] = useState("");

  const navigate = (nextPage, filter = "All") => {
    setPage(nextPage);

    if (nextPage === "Incident History") {
      setHistoryFilter(filter);
    }
  };

  // Normalize the backend response for the frontend.
  const normalizeIncident = (data, submittedLogs = "") => {
    const severity = String(data.severity || "UNKNOWN");

    const formattedSeverity =
      severity.charAt(0).toUpperCase() +
      severity.slice(1).toLowerCase();

    const possibleCauses = Array.isArray(data.possible_causes)
      ? data.possible_causes
      : [];

    return {
      id: data.incident_id,
      incident_id: data.incident_id,
      service: data.service || "payment-service",

      summary:
        data.summary ||
        `Incident analysis completed for ${data.service || "the submitted service"}.`,

      severity: formattedSeverity,
      status: data.verified ? "Resolved" : "Open",

      causes: possibleCauses.map((item) => ({
        cause: item.cause || "Unspecified cause",
        confidence: item.confidence || "Not provided",
        reason: item.reason || "",
      })),

      evidence: Array.isArray(data.evidence)
        ? data.evidence
        : [],

      checks: Array.isArray(data.recommended_checks)
        ? data.recommended_checks
        : [],

      historical_matches: Array.isArray(data.historical_matches)
        ? data.historical_matches
        : [],

      verified: Boolean(data.verified),
      confirmed_root_cause: data.actual_root_cause || "",
      verified_resolution: data.resolution || "",

      logs: submittedLogs,

      date: data.created_at
        ? new Date(data.created_at).toLocaleString()
        : new Date().toLocaleString(),

      created_at: data.created_at,
      rawResponse: data,
    };
  };

  // Analyze submitted logs through FastAPI.
  const analyse = async (inputLogs, service = "payment-service") => {
    if (!inputLogs || !inputLogs.trim()) {
      setAnalysisError("Please enter incident logs first.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError("");

    try {
      const response = await analyzeIncident(inputLogs, service);

      const result = normalizeIncident(response, inputLogs.trim());

      setIncident(result);

      setHistory((previous) => [
        result,
        ...previous.filter((item) => item.id !== result.id),
      ]);

      setPage("Analysis Result");
    } catch (error) {
      setAnalysisError(error.message || "Incident analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Verify an incident and save its resolution to Hindsight.
  const saveResolution = async (rootCause, resolution) => {
    if (!incident) return;

    setIsSaving(true);
    setVerificationError("");

    try {
      const response = await verifyIncident(
        incident.incident_id || incident.id,
        rootCause,
        resolution
      );

      if (!response.success || !response.stored_in_memory) {
        throw new Error(
          response.message ||
          "The backend did not confirm that the incident was saved to Hindsight."
        );
      }

      const updatedIncident = {
        ...incident,
        status: "Resolved",
        verified: true,
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
          incidentId: incident.incident_id || incident.id,
          summary: incident.summary,
          severity: incident.severity,
          service: incident.service,
          rootCause,
          resolution,
          created: response.verified_at
            ? new Date(response.verified_at).toLocaleString()
            : new Date().toLocaleString(),
        },
        ...previous.filter(
          (item) => item.incidentId !== (incident.incident_id || incident.id)
        ),
      ]);

      setPage("AI Memory");
    } catch (error) {
      setVerificationError(
        error.message || "Unable to verify and save the incident."
      );
    } finally {
      setIsSaving(false);
    }
  };

  // Retrieve the actual incident from FastAPI when View incident is clicked.
  const viewIncident = async (item) => {
    const incidentId = item.incidentId || item.incident_id;

    if (!incidentId) {
      setIncidentFetchError(
        "Original incident ID is missing from this memory record."
      );
      return;
    }

    setIsFetchingIncident(true);
    setIncidentFetchError("");

    try {
      const response = await getIncidentDetails(incidentId);

      const result = normalizeIncident(
        response,
        item.logs || ""
      );

      setIncident(result);

      setHistory((previous) => [
        result,
        ...previous.filter((existing) => existing.id !== result.id),
      ]);

      setPage("Analysis Result");
    } catch (error) {
      setIncidentFetchError(
        error.message || "Unable to retrieve incident details."
      );
    } finally {
      setIsFetchingIncident(false);
    }
  };

  const renderPage = () => {
    switch (page) {
      case "Dashboard":
        return (
          <Dashboard
            history={history}
            memory={memory}
            onNavigate={navigate}
            onAnalyseLogs={analyse}
            isAnalyzing={isAnalyzing}
            analysisError={analysisError}
          />
        );

      case "Analysis Result":
        return (
          <AnalysisResult
            incident={incident}
            onVerify={() => {
              setVerificationError("");
              setPage("Verify Resolution");
            }}
            onMemory={() => setPage("AI Memory")}
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
        return (
          <AIMemory
            memory={memory}
            onView={viewIncident}
            isLoading={isFetchingIncident}
            error={incidentFetchError}
          />
        );

      case "Verify Resolution":
        return (
          <VerifyResolution
            incident={incident}
            onSave={saveResolution}
            onCancel={() => setPage("Analysis Result")}
            isSaving={isSaving}
            error={verificationError}
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
            isAnalyzing={isAnalyzing}
            analysisError={analysisError}
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
