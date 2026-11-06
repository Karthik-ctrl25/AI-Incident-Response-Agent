# AI Incident Response Agent - Test Plan

## 1. Project Overview

The purpose of this test plan is to verify that the AI Incident Response Agent
can analyse application/server logs, identify possible causes, retrieve
relevant historical incidents from Hindsight, and recommend safe
investigation steps.

The system must only save an incident resolution to Hindsight after an
engineer confirms the actual root cause and verifies the resolution.

## 2. Test Environment

| Component | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| AI Model | Groq API |
| Agent Memory | Hindsight Cloud |
| Testing | Pytest + Manual Testing |
| Version Control | GitHub |

## 3. Sample Incident Test Cases

### TC-01: Database Connection Timeout

Input:
data/sample_logs/database_timeout.log

Expected results:
- Expected severity: HIGH
- Service: payments-service
- Possible cause: Database connection pool exhaustion.
- Evidence:
  - Connection pool usage reached 95%.
  - Connection timeout while acquiring database connection.
  - Database connection timeout after 15000ms.
  - HTTP 503 returned.
- Recommended checks:
  1. Inspect database connection pool usage.
  2. Check active and idle database connections.
  3. Review database server availability.
  4. Inspect connection timeout configuration.

Hindsight expectation:
A previously stored database connection incident should be recalled
if its symptoms and context are sufficiently similar.

### TC-02: High CPU and Memory Usage

Input:
data/sample_logs/high_cpu_memory.log

Expected results:
- Expected severity: HIGH
- Service: analytics-service
- Possible cause: Excessive resource consumption or inefficient processing.
- Evidence:
  - CPU utilization reached 88%.
  - Memory utilization reached 91%.
  - Memory threshold exceeded.
  - Garbage collection taking longer than expected.
  - Request latency exceeded 5000ms.
- Recommended checks:
  1. Inspect CPU and memory utilization.
  2. Identify resource-intensive processes.
  3. Review garbage collection activity.
  4. Inspect application performance metrics.

Hindsight expectation:
Recall only if a sufficiently similar resource-related incident exists.

### TC-03: Failed Deployment

Input:
data/sample_logs/failed_deployment.log

Expected results:
- Expected severity: HIGH
- Service: deployment-service
- Possible cause: Application startup or health-check failure.
- Evidence:
  - Container failed health check.
  - Application startup probe failed.
  - Container restart attempted.
  - Deployment marked as FAILED.
- Recommended checks:
  1. Inspect application startup logs.
  2. Verify health-check configuration.
  3. Check environment variables.
  4. Verify application dependencies.
  5. Review the deployment configuration.

Hindsight expectation:
Recall a previous deployment failure only if the stored incident
has relevant symptoms or evidence.

### TC-04: Authentication Failure

Input:
data/sample_logs/authentication_error.log

Expected results:
- Expected severity: MEDIUM
- Service: auth-service
- Possible cause: Invalid credentials or token validation failure.
- Evidence:
  - Invalid credentials provided.
  - Token validation failed.
  - Unauthorized request rejected.
  - HTTP 401 returned.
- Recommended checks:
  1. Verify authentication credentials.
  2. Inspect token validation configuration.
  3. Check token expiration and signing configuration.
  4. Review authentication service logs.

Hindsight expectation:
Recall only relevant authentication incidents.

### TC-05: Unrelated SMTP Incident

Input:
data/sample_logs/unrelated_incident.log

Expected results:
- Expected severity: MEDIUM
- Service: notification-service
- Possible cause: SMTP server unavailable or refusing connections.
- Evidence:
  - SMTP connection refused.
  - Email delivery failed.
  - Unable to send notification.
- Recommended checks:
  1. Verify SMTP server availability.
  2. Check SMTP host and port configuration.
  3. Inspect network connectivity.
  4. Verify mail service credentials.

Hindsight expectation:
This incident should NOT be incorrectly identified as a database
connection incident. If no relevant memory exists, the agent should
report that no sufficiently relevant historical incident was found.

## 4. Hindsight Memory Testing

### TC-06: Store a Verified Incident

1. Submit the database timeout log.
2. Review the AI-generated analysis.
3. Have an engineer confirm the actual root cause.
4. Enter the verified resolution.
5. Submit the resolution.
6. Verify that Hindsight retain is called successfully.

Expected result:
The verified incident and resolution are stored in Hindsight.

### TC-07: Recall a Similar Incident

1. Ensure a verified database incident is already stored.
2. Submit another similar database timeout log.
3. Check the returned similar incidents.

Expected result:
Hindsight should retrieve the earlier incident when relevant.
The interface should distinguish recalled information from current
log analysis.

### TC-08: Test an Unrelated Incident

1. Store a database timeout incident.
2. Submit the unrelated SMTP incident.
3. Inspect the recalled incidents.

Expected result:
The agent must not claim that the database incident is a matching
SMTP incident. It should indicate when no sufficiently relevant
memory is available.

### TC-09: Prevent Unverified Memory Storage

1. Submit an incident.
2. Generate an AI analysis.
3. Do not confirm the root cause or resolution.
4. Check whether a successful resolution was stored.

Expected result:
No unverified AI-generated resolution should be stored as a
confirmed successful fix.

## 5. API and Error Handling Tests

| Test ID | Scenario | Expected result |
|---|---|---|
| TC-10 | Empty log input | Validation error |
| TC-11 | Invalid request format | HTTP 422 or appropriate validation response |
| TC-12 | Invalid LLM response | Graceful error handling |
| TC-13 | Missing Groq API key | Configuration error |
| TC-14 | Missing Hindsight API key | Memory service error |
| TC-15 | Hindsight unavailable | Analysis handles memory failure gracefully |
| TC-16 | LLM timeout | Appropriate timeout response |
| TC-17 | Backend unavailable | Frontend displays an error |
| TC-18 | No matching historical incident | Empty memory result without fabricated matches |

## 6. End-to-End Integration Testing

Verify the following complete workflow:

1. Open the React application.
2. Submit a synthetic incident log.
3. Verify that React sends the request to FastAPI.
4. Verify that FastAPI validates the input.
5. Verify that the AI model analyses the log.
6. Verify that Hindsight recall is performed.
7. Verify that the results are displayed correctly.
8. Enter an engineer-confirmed root cause and resolution.
9. Submit the verified resolution.
10. Verify that Hindsight retain stores the incident.

Expected result:
The complete incident analysis and memory workflow should work
without data loss or misleading historical matches.

## 7. Regression Testing

After fixing a bug, repeat the relevant tests to ensure that
previously working features remain functional.

Important regression scenarios:

- Empty log submission.
- Similar historical incident recall.
- Unrelated incident recall.
- Engineer-confirmed resolution storage.
- Missing API keys.
- AI model timeout.
- Hindsight service outage.
- Frontend and backend communication.

## 8. Bug Reporting Format

For every identified bug, record:

- Bug ID
- Test case ID
- Bug description
- Steps to reproduce
- Expected result
- Actual result
- Screenshot or log evidence
- Status: Open / In Progress / Fixed / Verified

## 9. Test Completion Criteria

Testing is considered complete when:

- All five sample logs have been tested.
- Expected analysis fields are returned.
- Relevant historical incidents can be recalled.
- Unrelated incidents are not presented as confirmed matches.
- Only engineer-verified resolutions are stored.
- API error cases have been tested.
- The frontend-to-backend workflow works.
- Critical bugs have been fixed and retested.

## 10. Important Testing Note

Expected severity and possible root causes in this document are
test expectations, not confirmed diagnoses. The application must
use the supplied log evidence and must not present suspected causes
as verified facts.

All sample logs are synthetic and intended for demonstration
and software testing only.
