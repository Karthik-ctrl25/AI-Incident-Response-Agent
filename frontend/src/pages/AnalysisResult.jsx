import React from "react";

import {
  FileText,
  AlertTriangle,
  ListChecks,
  ShieldCheck,
  BrainCircuit
} from "lucide-react";

export default function AnalysisResult({
  incident,
  onVerify,
  onMemory
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

  return (
    <div className="result-page">
      <div className="page-heading">
        <div>
          <h2>Incident Analysis Result</h2>
          <p>AI analysis with incident context</p>
        </div>

        <span className="incident-id">
          Incident ID: {incident.id}
        </span>
      </div>

      <div className="result-grid">
        <section className="panel">
          <h3>
            <FileText size={17} />
            Incident Summary
          </h3>

          <p>{incident.summary}</p>

          <h3>
            <AlertTriangle size={17} />
            Suspected Root Causes
          </h3>

          <ul>
            {incident.causes.map((cause) => (
              <li key={cause}>{cause}</li>
            ))}
          </ul>

          <h3>
            <ListChecks size={17} />
            Recommended Investigation Steps
          </h3>

          <ol>
            {incident.checks.map((check) => (
              <li key={check}>{check}</li>
            ))}
          </ol>
        </section>

        <section className="panel">
          <div className="severity-box">
            <span>Severity</span>
            <b className="severity-pill">
              {incident.severity}
            </b>
          </div>

          <h3>
            <FileText size={17} />
            Evidence (from logs)
          </h3>

          <div className="evidence">
            {incident.evidence.map((line, index) => (
              <p key={index}>{line}</p>
            ))}
          </div>
        </section>
      </div>

      <div className="page-actions">
        <button
          className="analyse-submit"
          onClick={onVerify}
        >
          <ShieldCheck size={15} />
          Verify and Save Resolution
        </button>

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