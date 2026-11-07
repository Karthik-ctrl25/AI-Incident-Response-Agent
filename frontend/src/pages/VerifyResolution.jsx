import React, { useState } from "react";

import {
  CheckCircle2,
  Save,
  X
} from "lucide-react";

export default function VerifyResolution({
  incident,
  onSave,
  onCancel
}) {
  const [cause, setCause] = useState(
    incident?.rootCause || ""
  );

  const [resolution, setResolution] = useState(
    incident?.resolution || ""
  );

  if (!incident) {
    return (
      <div className="panel">
        No incident selected.
      </div>
    );
  }

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
            />
          </label>

          <label>
            Verified Resolution <em>*</em>

            <textarea
              value={resolution}
              onChange={(event) => setResolution(event.target.value)}
              placeholder="Describe the fix that was applied and verified..."
            />
          </label>

          <div className="page-actions">
            <button
              className="analyse-submit"
              disabled={!cause.trim() || !resolution.trim()}
              onClick={() => onSave(cause, resolution)}
            >
              <Save size={15} />
              Confirm & Save to Hindsight
            </button>

            <button
              className="clear-button"
              onClick={onCancel}
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
        </aside>
      </div>
    </div>
  );
}