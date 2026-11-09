
import React from "react";

import {
  FileText,
  AlertTriangle,
  ListChecks,
  ShieldCheck,
  BrainCircuit,
  Clock,
  CheckCircle2,
  Search,
} from "lucide-react";

export default function AnalysisResult({
  incident,
  onVerify,
  onMemory,
}) {
  if (!incident) {
    return (
      <section className="panel">
        <h2>No analysis available</h2>
        <p className="muted">
          Submit logs to generate an incident analysis.
        </p>
      </section>
    );
  }

  const causes = incident.causes || [];
  const evidence = incident.evidence || [];
  const checks = incident.checks || [];
  const historicalMatches = incident.historical_matches || [];

  const isVerified = incident.verified || incident.status === "Resolved";

  return (
    <div className="result-page">

      {/* PAGE HEADING */}
      <div className="page-heading">
        <div>
          <h2>Incident Analysis Result</h2>
          <p>
            AI-powered incident investigation and historical intelligence
          </p>
        </div>

        <span className="incident-id">
          Incident ID: {incident.id}
        </span>
      </div>

      {/* INCIDENT INFORMATION */}
      <div className="result-grid">

        {/* LEFT PANEL */}
        <section className="panel">

          <h3>
            <FileText size={17} />
            Incident Summary
          </h3>

          <p>
            {incident.summary || "Incident analysis completed. Review the findings below."}
          </p>

          <h3>
            <AlertTriangle size={17} />
            Possible Root Causes
          </h3>

          {causes.length > 0 ? (
            <div className="analysis-causes">
              {causes.map((item, index) => {
                const cause =
                  typeof item === "string" ? item : item.cause;

                const confidence =
                  typeof item === "object"
                    ? item.confidence
                    : null;

                const reason =
                  typeof item === "object"
                    ? item.reason
                    : null;

                return (
                  <div className="analysis-cause-item" key={index}>
                    <strong>{index + 1}. {cause}</strong>

                    {confidence && (
                      <p>
                        <b>Confidence:</b> {confidence}
                      </p>
                    )}

                    {reason && (
                      <p>{reason}</p>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p>No possible causes were returned.</p>
          )}

          <h3>
            <ListChecks size={17} />
            Recommended Investigation Steps
          </h3>

          {checks.length > 0 ? (
            <ol>
              {checks.map((check, index) => (
                <li key={index}>{check}</li>
              ))}
            </ol>
          ) : (
            <p>No investigation steps were returned.</p>
          )}

        </section>

        {/* RIGHT PANEL */}
        <section className="panel">

          <div className="severity-box">
            <span>Severity</span>

            <b className="severity-pill">
              {incident.severity || "Unknown"}
            </b>
          </div>

          {isVerified && (
            <p>
              <CheckCircle2 size={16} />
              Verified incident
            </p>
          )}

          <h3>
            <FileText size={17} />
            Evidence from Logs
          </h3>

          <div className="evidence">
            {evidence.length > 0 ? (
              evidence.map((line, index) => (
                <p key={index}>{line}</p>
              ))
            ) : (
              <p>No evidence returned.</p>
            )}
          </div>

          <h3>
            <Clock size={17} />
            Incident Information
          </h3>

          <p>
            <b>Service:</b> {incident.service || "Unknown"}
          </p>

          <p>
            <b>Status:</b> {incident.status || "Open"}
          </p>

          <p>
            <b>Created:</b> {incident.date || "Not available"}
          </p>

        </section>
      </div>

      {/* HISTORICAL HINDSIGHT MATCHES */}
      <section className="panel historical-matches-panel">

        <h3>
          <BrainCircuit size={18} />
          Historical Matches from Hindsight
        </h3>

        <p>
          Previously stored incidents that may help investigate
          the current issue.
        </p>

        {historicalMatches.length > 0 ? (
          <div className="historical-match-list">

            {historicalMatches.map((match, index) => (
              <div
                className="historical-match-item"
                key={match.incident_id || index}
              >
                <strong>
                  {match.incident_id || `Historical Incident ${index + 1}`}
                </strong>

                <p>
                  <b>Service:</b> {match.service || "Unknown"}
                </p>

                <p>
                  <b>Previous Root Cause:</b>{" "}
                  {match.root_cause || "Not available"}
                </p>

                <p>
                  <b>Previous Resolution:</b>{" "}
                  {match.resolution || "Not available"}
                </p>

                <p>
                  <b>Similarity Context:</b>{" "}
                  {match.similarity_context || "Not available"}
                </p>
              </div>
            ))}

          </div>
        ) : (
          <div className="empty-state">
            <Search size={25} />
            <p>No historical matches found.</p>
            <span>
              Similar verified incidents will appear here when available.
            </span>
          </div>
        )}

      </section>

      {/* ACTION BUTTONS */}
      <div className="page-actions">

        {!isVerified && (
          <button
            className="analyse-submit"
            onClick={onVerify}
          >
            <ShieldCheck size={15} />
            Verify and Save Resolution
          </button>
        )}

        <button
          className="secondary-action"
          onClick={onMemory}
        >
          <BrainCircuit size={15} />
          View AI Memory
        </button>

      </div>

    </div>
  );
}
