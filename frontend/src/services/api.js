
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  "https://three-facts-juggle.loca.lt"
).replace(/\/+$/, "");

// Common API request handler
async function apiRequest(endpoint, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "bypass-tunnel-reminder": "true",
        ...options.headers,
      },
    });
  } catch (error) {
    throw new Error(
      `Cannot connect to the backend at ${API_BASE_URL}. Check the backend and tunnel.`
    );
  }

  const responseText = await response.text();

  let data;

  try {
    data = responseText ? JSON.parse(responseText) : {};
  } catch {
    if (response.status === 511) {
      throw new Error(
        "LocalTunnel verification blocked the API request. Check the tunnel URL and bypass header."
      );
    }

    throw new Error(
      `Backend returned a non-JSON response (HTTP ${response.status}).`
    );
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

// 1. Check backend health
export async function checkBackendHealth() {
  return apiRequest("/");
}

// 2. Analyse incident logs
export async function analyzeIncident(
  logs,
  service = "unknown-service"
) {
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

// 3. Verify incident and store resolution
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

// 4. Retrieve incident details
export async function getIncidentDetails(incidentId) {
  if (!incidentId) {
    throw new Error("Incident ID is missing.");
  }

  return apiRequest(
    `/api/incidents/${encodeURIComponent(incidentId)}`
  );
}
