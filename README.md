# AI Incident Response Agent

An AI-powered incident response system designed to help engineers analyze application and server logs, investigate potential failures, and learn from previously resolved incidents.

## Overview

Diagnosing production incidents can be time-consuming. Engineers often need to inspect large volumes of logs, identify error patterns, investigate possible root causes, and search for previous solutions.

The AI Incident Response Agent aims to simplify this process by combining AI-based log analysis with persistent incident memory powered by **Hindsight**.

The system is designed to:
- Analyze application and server logs.
- Identify potential root causes and incident severity.
- Retrieve relevant historical incidents.
- Recommend investigation steps and possible resolutions.
- Retain incident resolutions only after engineer verification.

## Key Features

- **Log analysis:** Examine application logs to identify errors and abnormal behavior.
- **AI-assisted diagnosis:** Generate potential root causes and recommended investigation steps.
- **Historical incident recall:** Use Hindsight to retrieve information from previously resolved incidents.
- **Verified memory:** Store incident resolutions only after an engineer confirms the root cause and resolution.
- **Testing and validation:** Use synthetic incident logs and automated tests to evaluate expected behavior.

## System Architecture

The planned system consists of the following components:

| Component | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| AI model | Groq API |
| Agent memory | Hindsight Cloud |
| Testing | Pytest + Manual Testing |
| Version control | Git + GitHub |

### Intended workflow

1. An engineer submits application or server logs through the frontend.
2. The backend receives the logs and initiates AI-based analysis.
3. Hindsight retrieves potentially relevant historical incidents.
4. The AI uses the available context to generate a diagnosis and recommendations.
5. The engineer reviews and verifies the suggested resolution.
6. Only verified incident information is retained in Hindsight for future recall.

## Hindsight Integration

Hindsight provides persistent memory for the incident response system.

The backend memory service is designed around two primary operations:

- **Retain:** Store verified incident details, including logs, root cause, resolution, service name, and severity.
- **Recall:** Retrieve potentially similar incidents based on incoming logs.

An important safety rule is enforced: unverified incident resolutions must not be stored as confirmed knowledge.

The Hindsight configuration uses these environment variables:

- `HINDSIGHT_API_KEY`
- `HINDSIGHT_BASE_URL`
- `HINDSIGHT_BANK_ID`

Never commit real API keys or credentials to the repository.

## Project Structure

```text
AI-Incident-Response-Agent/
├── backend/
│   ├── app/
│   │   └── services/
│   │       └── hindsight_service.py
│   ├── tests/
│   │   ├── test_hindsight.py
│   │   └── test_hindsight_unit.py
│   ├── requirements.txt
│   └── .env.example
├── data/
│   └── sample_logs/
├── docs/
│   ├── TEST_PLAN.md
│   └── DEMO_SCRIPT.md
├── tests/
├── .gitignore
└── README.md
```

## Sample Incident Logs

The project includes synthetic logs representing different incident scenarios:

- Database connection timeout
- Authentication errors
- Failed deployment
- High CPU and memory usage
- Unrelated incidents for testing memory relevance

These samples help evaluate the system's ability to identify relevant evidence and avoid incorrectly associating unrelated incidents.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/nadeem6456/AI-Incident-Response-Agent.git
cd AI-Incident-Response-Agent
```

### 2. Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
python -m pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create a local environment file using the example:

```bash
cp backend/.env.example backend/.env
```

Add your own valid Hindsight API key to `backend/.env`.

Do not share or commit this file.

## Testing

The project includes automated unit tests for the Hindsight memory service.

Run the unit tests from the project root:

```bash
PYTHONPATH=backend pytest -v backend/tests/test_hindsight_unit.py
```

The tests cover:

- Successful storage of verified incidents.
- Rejection of unverified incidents.
- Validation of required incident information.
- Recall of similar incidents.
- Rejection of empty logs.
- Handling of Hindsight errors.
- Missing API key validation.
- Proper connection closure.

Additional test scenarios and expected outcomes are documented in:

- `docs/TEST_PLAN.md`
- `tests/test_memory_flow.md`

## Current Development Status

The project is under active development.

| Area | Status |
|---|---|
| Hindsight memory service | Implemented |
| Synthetic incident log samples | Prepared |
| Test plan and QA documentation | Prepared |
| Hindsight unit tests | Implemented |
| FastAPI and frontend integration | Awaiting team integration |
| End-to-end validation | Pending integration |
| Final demonstration | Pending integration |

Full application startup instructions, API endpoint documentation, screenshots, and end-to-end results will be added after integration and verification.

## Future Improvements

- Improve incident classification and root-cause analysis.
- Enhance relevance of historical incident retrieval.
- Add more incident log formats and test scenarios.
- Expand automated integration and end-to-end testing.
- Improve the engineer review and resolution confirmation workflow.

## Contributors

Developed collaboratively by the project team. Contributions and responsibilities are maintained through the project repository.

## License

Add the project's chosen license here before public release.
