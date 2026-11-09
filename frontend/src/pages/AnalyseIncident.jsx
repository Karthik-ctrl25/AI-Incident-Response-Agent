import React, { useRef, useState } from "react";

import {
  Clipboard,
  Upload,
  Play,
  Trash2,
  FileText,
  AlertCircle
} from "lucide-react";

export default function AnalyseIncident({
  logs,
  setLogs,
  onAnalyse
}) {
  const input = useRef(null);
  const [notice, setNotice] = useState("");

  const paste = async () => {
    try {
      const text = await navigator.clipboard.readText();

      if (text) {
        setLogs((previous) =>
          previous ? previous + "\n" + text : text
        );
      } else {
        setNotice("Clipboard is empty.");
      }
    } catch {
      setNotice(
        "Clipboard access unavailable. Use Ctrl+V in the editor."
      );
    }
  };

  const upload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!/\.(log|txt)$/i.test(file.name)) {
      setNotice("Choose a .log or .txt file.");
      event.target.value = "";
      return;
    }

    try {
      setLogs(await file.text());
      setNotice(`${file.name} loaded.`);
    } catch {
      setNotice("Unable to read this file.");
    }

    event.target.value = "";
  };

  return (
    <div className="analyse-page">
      <div className="page-heading">
        <div>
          <h2>Analyse a New Incident</h2>
          <p>
            Paste your server/application logs or upload a log
            file to begin AI-powered analysis.
          </p>
        </div>
      </div>

      <section className="log-panel">
        <div className="log-toolbar">
          <div className="log-file-info">
            <FileText size={17} />
            Incident log input
          </div>

          <div className="log-actions">
            <button
              className="secondary-action"
              onClick={paste}
            >
              <Clipboard size={15} />
              Paste Logs
            </button>

            <button
              className="secondary-action"
              onClick={() => input.current?.click()}
            >
              <Upload size={15} />
              Upload File
            </button>

            <input
              ref={input}
              hidden
              type="file"
              accept=".log,.txt,text/plain"
              onChange={upload}
            />
          </div>
        </div>

        <div className="log-editor">
          <div className="editor-topline">
            <i className="editor-dot" />
            SERVER LOGS
            <span className="editor-language">TEXT</span>
          </div>

          <textarea
            value={logs}
            onChange={(event) => setLogs(event.target.value)}
            spellCheck="false"
            placeholder={`Paste your application or server logs here...

Example:

2026-11-07 10:24:12 ERROR Database connection failed
2026-11-07 10:24:17 WARN Database service not responding`}
          />

          <div className="editor-footer">
            <span>{logs.length} characters</span>
            <span>
              {logs.split("\n").filter(Boolean).length} lines
            </span>
          </div>
        </div>

        {notice && (
          <p className="notice">
            <AlertCircle size={14} />
            {notice}
          </p>
        )}

        <div className="analyse-controls">
          <button
            className="analyse-submit"
            onClick={() => {
              if (!logs.trim()) {
                setNotice("Please paste or upload logs first.");
                return;
              }

              setNotice("");
              onAnalyse();
            }}
          >
            <Play size={14} fill="currentColor" />
            Analyse Incident
          </button>

          <button
            className="clear-button"
            onClick={() => {
              setLogs("");
              setNotice("");
            }}
          >
            <Trash2 size={14} />
            Clear
          </button>
        </div>
      </section>
    </div>
  );
}