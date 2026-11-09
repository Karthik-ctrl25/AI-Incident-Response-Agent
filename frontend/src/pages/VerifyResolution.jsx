
import React, { useState } from "react";

import {
  CheckCircle2,
  Save,
  X,
  AlertTriangle,
  Loader2,
} from "lucide-react";

export default function VerifyResolution({
  incident,
  onSave,
  onCancel,
  isSaving = false,
  error = "",
}) {
  const [cause, setCause] = useState(
    incident?.confirmed_root_cause || ""
  );

  const [resolution, setResolution] = useState(
    incident?.verified_resolution || ""
  );

  if (!incident) {
    return (
      <div className="panel">
        No incident selected.
      </div>
    );
  }

  const handleSubmit = () => {
    if (!cause.trim() || !resolution.trim() || isSaving) {
      return;
    }

    onSave(cause, resolution);
  };

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Verify and Save Resolution</h2>
          <p>
            Confirm the actual root cause and resolution after investigation.
          </p>
        </div>
      </div>

      <div className="verify-grid">

        <section className="panel verify-form">

          <label>
            Confirmed Root Cause <em>*</em>

            <textarea
              value={cause}
              onChange={(event) => setCause(event.target.value)}
              placeholder="Enter the confirmed root cause..."
              disabled={isSaving}
            />
          </label>

          <label>
            Verified Resolution <em>*</em>

            <textarea
              value={resolution}
              onChange={(event) => setResolution(event.target.value)}
              placeholder="Describe the fix that was applied and verified..."
              disabled={isSaving}
            />
          </label>

          {error && (
            <div
              className="chat-hint"
              role="alert"
            >
              <AlertTriangle size={16} />
              <span>{error}</span>
            </div>
          )}

          {isSaving && (
            <div className="chat-hint">
              <Loader2 size={16} className="spin-icon" />
              <span>
                Saving verified incident to Hindsight...
              </span>
            </div>
          )}

          <div className="page-actions">

            <button
              type="button"
              className="analyse-submit"
              disabled={
                !cause.trim() ||
                !resolution.trim() ||
                isSaving
              }
              onClick={handleSubmit}
            >
              {isSaving ? (
                <>
                  <Loader2 size={15} className="spin-icon" />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={15} />
                  Confirm & Save to Hindsight
                </>
              )}
            </button>

            <button
              type="button"
              className="clear-button"
              onClick={onCancel}
              disabled={isSaving}
            >
              <X size={15} />
              Cancel
            </button>

          </div>
        </section>

        <aside className="panel verify-note">

          <CheckCircle2 size={35} />

          <h3>Incident {incident.id}</h3>

          <p>
            Only save the root cause and resolution after
            they have been verified by the engineer.
          </p>

          <p>
            The backend will store the verified resolution
            in Hindsight memory after successful confirmation.
          </p>

        </aside>

      </div>
    </div>
  );
}
