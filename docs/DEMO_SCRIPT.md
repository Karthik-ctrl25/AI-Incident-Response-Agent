# AI Incident Response Agent - Demo Script

**Target duration:** 2–5 minutes

## 1. Introduction (20–30 seconds)

Introduce the AI Incident Response Agent.

Explain that the system helps engineers investigate incidents by analyzing
application logs, identifying possible causes, and recalling relevant
previous incidents using Hindsight memory.

## 2. Project Architecture (30 seconds)

Briefly explain the workflow:

1. React frontend accepts incident logs from the engineer.
2. FastAPI backend receives the submitted logs.
3. LLM analyzes the logs and suggests possible causes.
4. Hindsight retrieves relevant previous incidents.
5. The application displays the analysis and investigation suggestions.
6. The engineer verifies the actual cause and resolution.
7. Only engineer-confirmed resolutions are stored in Hindsight.

## 3. Demonstrate Incident Analysis (45–60 seconds)

Use the sample log:

data/sample_logs/database_timeout.log

Explain the important evidence:
- Database connection pool usage reaches 95%.
- Connection acquisition times out.
- Transactions fail.
- The application returns HTTP 503.

Expected analysis:
- Possible severity: HIGH.
- Affected service: payments-service.
- Possible cause: database connection pool exhaustion
  or database connectivity problems.

Show the AI-generated analysis and investigation suggestions.

## 4. Demonstrate Hindsight Recall (30–45 seconds)

Submit an incident similar to a previously stored incident.

Explain how Hindsight retrieves relevant historical information.

Show how previous incident information can support the current
investigation without replacing engineer verification.

## 5. Demonstrate Engineer Confirmation (30–45 seconds)

Explain that AI suggestions are not automatically treated as verified facts.

The engineer reviews the suggested cause and resolution.

After confirmation, the verified resolution is stored in Hindsight
for possible use in future incidents.

## 6. Testing Demonstration (30–45 seconds)

Show the sample logs in:

data/sample_logs/

Briefly explain the test coverage:
- Database connection timeout.
- High CPU and memory usage.
- Failed deployment.
- Authentication failure.
- Unrelated SMTP incident.

Mention that testing also covers empty input, unavailable services,
irrelevant memories, and unverified resolutions.

## 7. Conclusion (15–20 seconds)

Conclude by explaining that the project combines log analysis,
historical incident memory, and engineer verification to support
more informed incident investigation.

Thank the audience.
