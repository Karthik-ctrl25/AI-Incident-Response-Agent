
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Common API request handler
async function apiRequest(endpoint, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch (error) {
    throw new Error(
      "Cannot connect to the backend. Please check whether FastAPI is running at " +
      API_BASE_URL
    );
  }

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The backend returned an invalid response.");
  }

  if (!response.ok) {
    const message =
      data.detail ||
      data.message ||
      `Request failed with status ${response.status}`;

    throw new Error(
      typeof message === "string"
        ? message
        : JSON.stringify(message)
    );
  }

  return data;
}

// 1. Check backend connection
export async function checkBackendHealth() {
  return apiRequest("/");
}

// 2. Analyse incident logs
export async function analyzeIncident(logs, service = "unknown-service") {
  if (!logs || !logs.trim()) {
    throw new Error("Please enter server logs before submitting.");
  }

  if (logs.length > 50000) {
    throw new Error("Logs cannot exceed 50,000 characters.");
  }

  return apiRequest("/api/incidents/analyze", {
    method: "POST",
    body: JSON.stringify({
      logs: logs.trim(),
      service: service.trim() || "unknown-service",
    }),
  });
}

// 3. Submit verified incident resolution
export async function verifyIncident(
  incidentId,
  actualRootCause,
  resolution
) {
  if (!incidentId) {
    throw new Error("Incident ID is missing.");
  }

  if (!actualRootCause.trim()) {
    throw new Error("Please enter the confirmed root cause.");
  }

  if (!resolution.trim()) {
    throw new Error("Please enter the verified resolution.");
  }

  return apiRequest(
    `/api/incidents/${encodeURIComponent(incidentId)}/verify`,
    {
      method: "POST",
      body: JSON.stringify({
        actual_root_cause: actualRootCause.trim(),
        resolution: resolution.trim(),
        verified: true,
      }),
    }
  );
}

// 4. Retrieve complete incident details
export async function getIncidentDetails(incidentId) {
  if (!incidentId) {
    throw new Error("Incident ID is missing.");
  }

  return apiRequest(
    `/api/incidents/${encodeURIComponent(incidentId)}`
  );
}
