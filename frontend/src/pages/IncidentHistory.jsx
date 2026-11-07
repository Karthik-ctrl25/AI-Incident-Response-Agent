import React, { useMemo, useState } from "react";

import { Search, Eye } from "lucide-react";

export default function IncidentHistory({
  history = [],
  onView
}) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("All");

  const rows = useMemo(() => {
    return history.filter((item) => {
      const matchesStatus =
        status === "All" || item.status === status;

      const searchText =
        `${item.id} ${item.summary} ${item.severity}`.toLowerCase();

      return (
        matchesStatus &&
        searchText.includes(query.toLowerCase())
      );
    });
  }, [history, query, status]);

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Incident History</h2>
          <p>
            All analysed incidents with their status and resolutions
          </p>
        </div>

        <div className="table-tools">
          <label>
            <Search size={14} />

            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by ID or keyword"
            />
          </label>

          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
          >
            <option>All</option>
            <option>Resolved</option>
            <option>Investigating</option>
          </select>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Incident ID</th>
              <th>Incident Summary</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Date & Time</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>

                <td>{item.summary.slice(0, 65)}...</td>

                <td>
                  <span className="severity-pill">
                    {item.severity}
                  </span>
                </td>

                <td>
                  <span
                    className={
                      item.status === "Resolved"
                        ? "resolved-label"
                        : "investigating-label"
                    }
                  >
                    {item.status}
                  </span>
                </td>

                <td>{item.created}</td>

                <td>
                  <button
                    className="table-view"
                    onClick={() => onView(item)}
                  >
                    <Eye size={13} />
                    View
                  </button>
                </td>
              </tr>
            ))}

            {!rows.length && (
              <tr>
                <td colSpan="6" className="table-empty">
                  No matching incidents. Analyse logs to create history.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}