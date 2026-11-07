import React from "react";

import {
  BrainCircuit,
  Calendar,
  ArrowRight
} from "lucide-react";

export default function AIMemory({ memory = [], onView }) {
  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Hindsight Memory Intelligence</h2>
          <p>
            Previously verified incidents retained for future investigation
          </p>
        </div>
      </div>

      <div className="memory-banner">
        <BrainCircuit size={19} />
        Local session memory · {memory.length} verified incident(s)
      </div>

      {memory.length ? (
        memory.map((item) => (
          <article className="panel memory-card" key={item.id}>
            <div className="section-heading">
              <h3>
                {item.id} · {item.severity}
              </h3>

              <span className="resolved-label">
                Verified resolution
              </span>
            </div>

            <p>{item.summary}</p>

            <p>
              <b>Root cause:</b> {item.rootCause}
            </p>

            <p>
              <b>Verified resolution:</b> {item.resolution}
            </p>

            <div className="memory-meta">
              <span>
                <Calendar size={13} />
                {item.created}
              </span>

              <button
                className="secondary-action"
                onClick={() => onView(item)}
              >
                View incident
                <ArrowRight size={14} />
              </button>
            </div>
          </article>
        ))
      ) : (
        <div className="panel empty-state">
          <BrainCircuit size={28} />
          <p>No verified historical incidents yet.</p>
          <span>
            Verify and save an incident resolution to create a memory record.
          </span>
        </div>
      )}
    </div>
  );
}