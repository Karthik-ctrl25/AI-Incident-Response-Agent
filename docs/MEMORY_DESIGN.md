# Hindsight Memory Design

## 1. Overview

The AI Incident Response Agent uses Hindsight Cloud as its long-term incident memory system.

The purpose of this integration is to allow the agent to learn from previously verified incidents and use historical knowledge when investigating new incidents.

Technology:
- Hindsight Cloud
- hindsight-client
- Python
- python-dotenv

## 2. Memory Architecture

The memory system contains two primary operations.

### Retain

Stores engineer-verified incidents.

Information stored:
- Incident ID
- Service name
- Severity
- Original logs
- Verified root cause
- Successful resolution
- Verification timestamp

Only verified incidents are permitted to enter long-term memory.

### Recall

Retrieves historical incidents relevant to newly submitted logs.

The recall query considers:
- Error messages
- Exception types
- Stack traces
- Failed components
- Database failures
- Network failures
- Historical root causes
- Previous resolutions

Retrieved memories are candidates for investigation and must be evaluated before being recommended.

## 3. Memory Bank Configuration

Memory Bank ID:

incident-response-memory

Memory Bank Name:

AI Incident Response Agent

Cloud API:

https://api.hindsight.vectorize.io

Credentials are configured through environment variables.

## 4. Environment Variables

HINDSIGHT_API_KEY

HINDSIGHT_BASE_URL

HINDSIGHT_BANK_ID

Secrets must never be committed to GitHub.

## 5. Service Implementation

File:

backend/app/services/hindsight_service.py

Main class:

HindsightMemoryService

Methods:

- store_verified_incident()
- recall_similar_incidents()
- close()

## 6. Incident Storage Workflow

1. An engineer reviews an incident.
2. The actual root cause is identified.
3. The resolution is confirmed.
4. The backend calls store_verified_incident().
5. Hindsight processes and stores the incident.
6. The incident becomes available for future recall.

Unverified AI predictions must not be stored.

## 7. Incident Retrieval Workflow

1. A user submits new server/application logs.
2. The Groq model analyses the logs.
3. The backend calls recall_similar_incidents().
4. Hindsight retrieves relevant historical memories.
5. Groq evaluates the retrieved incidents against the current logs.
6. The system presents possible causes, supporting evidence and investigation steps.

## 8. Safety Rules

- Never store unverified incidents.
- Never expose API credentials.
- Never automatically execute server repairs.
- Never treat recalled memories as guaranteed root causes.
- Engineers must verify suggested resolutions.
- Unrelated historical incidents must not be recommended.

## 9. Testing Strategy

Three primary tests are required.

Test A: Store a verified PostgreSQL connection incident.

Test B: Submit similar PostgreSQL connection logs and check whether the previous incident is retrieved.

Test C: Submit unrelated Java memory-error logs and verify that the PostgreSQL incident is not recommended.

### Initial Test Results

| Test | Result | Observation |
|---|---|---|
| Store verified incident | PASS | INC-001 stored successfully |
| Similar incident recall | PASS | PostgreSQL incident retrieved |
| Unrelated incident recall | NEEDS IMPROVEMENT | PostgreSQL incident also returned for Java memory error |

### Improvement Required

Hindsight recall can return loosely related memories.

A relevance validation stage must be implemented
before historical incidents are passed to Groq.

The system must not recommend previous resolutions
without checking their relevance to the current incident.

## 10. Future Improvements

- Evaluate recall precision and relevance.
- Introduce a structured incident evaluation stage.
- Track successful versus unsuccessful recommendations.
- Improve memory retrieval using service and error metadata.
- Measure how often historical resolutions help solve recurring incidents.

## 11. Expected Outcome

The agent should improve its incident investigation recommendations by retrieving and learning from previously verified incidents.

Hindsight provides persistent memory across separate incident investigations.