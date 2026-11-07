# Hindsight Memory Flow Tests

## Objective
Verify that the AI Incident Response Agent recalls relevant previous
incidents and stores only engineer-confirmed resolutions.

## Test Case 1: Store a Verified Resolution
- Submit a sample incident log.
- Allow the AI to analyze the incident.
- Engineer reviews the suggested cause and resolution.
- Engineer confirms the resolution.
- Expected: The confirmed incident and resolution are stored in Hindsight.

## Test Case 2: Recall a Similar Incident
- Submit an incident similar to a previously confirmed incident.
- Expected: Hindsight retrieves the relevant previous incident.
- Expected: The AI uses the retrieved information as supporting context.

## Test Case 3: Do Not Store Unverified Resolutions
- Submit an incident.
- Allow the AI to suggest a cause and resolution.
- Do not let the engineer confirm the resolution.
- Expected: The incident resolution is NOT stored in Hindsight.

## Test Case 4: Unrelated Incident
- Submit an SMTP connection failure.
- Assume the stored memory contains a database connection timeout.
- Expected: The system does not incorrectly treat the database incident
  as an exact match for the SMTP incident.

## Test Case 5: No Previous Memory
- Submit an incident when Hindsight has no relevant stored incidents.
- Expected: The system provides a fresh analysis without inventing
  previous incidents.

## Test Case 6: Hindsight Service Unavailable
- Make Hindsight unavailable during analysis.
- Expected: The application handles the failure gracefully.
- Expected: The user receives an appropriate error or fallback response.

## Test Case 7: Duplicate Resolution
- Submit an already confirmed incident resolution again.
- Expected: The system handles duplicate storage according to the
  agreed backend design.

## Important Rules
- AI-generated suggestions are not verified facts.
- Only engineer-confirmed resolutions may be retained.
- Retrieved memories must be relevant to the current incident.
- All memory tests must use synthetic incident data.
