"""
Hackathon Demonstration Script: AI Incident Response Agent (Hack With Bangalore 4.0)
Demonstrates:
  Step 1: First Incident Analysis (no prior memory)
  Step 2: Engineer Verification & Retention in Hindsight Cloud
  Step 3: Second Incident Analysis (Hindsight Memory Recall & Improved AI Recommendations)
"""

import json
import time
import requests

BASE_URL = "http://localhost:8000"

SAMPLE_LOG_1 = """2026-11-06 10:00:01 INFO [payments-service] Application started
2026-11-06 10:00:05 INFO [payments-service] Connecting to database
2026-11-06 10:00:10 WARN [payments-service] Database connection pool usage: 95%
2026-11-06 10:00:15 ERROR [payments-service] Connection timeout while acquiring database connection
2026-11-06 10:00:16 ERROR [payments-service] Failed to execute transaction
2026-11-06 10:00:20 WARN [payments-service] Retrying database connection
2026-11-06 10:00:25 ERROR [payments-service] Database connection timeout after 15000ms
2026-11-06 10:00:30 ERROR [payments-service] Request failed with HTTP 503"""

SAMPLE_LOG_2 = """2026-11-06 16:30:10 WARN [payments-service] Connection pool saturated: 98%
2026-11-06 16:30:15 ERROR [payments-service] OperationalError: timeout acquiring connection from pool
2026-11-06 16:30:20 ERROR [payments-service] Failed to complete payment checkout
2026-11-06 16:30:25 ERROR [payments-service] HTTP 503 Service Unavailable"""


def print_banner(title: str):
    print("\n" + "=" * 70)
    print(f" {title.upper()} ")
    print("=" * 70)


def run_demo():
    print_banner("Hack With Bangalore 4.0 - AI Incident Response Agent Demo")

    # 0. Health check
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"[OK] Backend health check: {r.status_code} - {r.json()['message']}")
    except Exception as e:
        print(f"[ERROR] Could not connect to {BASE_URL}. Ensure the backend is running.")
        print(f"Run: python -m uvicorn app.main:app --app-dir backend --port 8000")
        return

    # 1. First Incident: Initial Analysis
    print_banner("Step 1: First Occurrence - Submit Incident Logs")
    print("Submitting payments-service database timeout logs...")

    resp = requests.post(
        f"{BASE_URL}/api/incidents/analyze",
        json={"logs": SAMPLE_LOG_1, "service": "payments-service"},
        timeout=30
    )
    if resp.status_code != 200:
        print(f"[FAIL] Incident analysis failed: {resp.status_code} - {resp.text}")
        return

    data1 = resp.json()
    inc_id_1 = data1["incident_id"]
    print(f"Incident ID Generated: {inc_id_1}")
    print(f"Assessed Severity:     {data1['severity']}")
    print(f"Historical Matches:    {len(data1['historical_matches'])} (No prior verified memory)")
    print("\nAI Possible Causes:")
    for c in data1["possible_causes"]:
        print(f"  - [{c['confidence'].upper()}] {c['cause']}: {c['reason']}")
    print("\nDiagnostic Evidence:")
    for ev in data1["evidence"]:
        print(f"  * {ev}")
    print("\nRecommended Checks:")
    for chk in data1["recommended_checks"]:
        print(f"  -> {chk}")

    # 2. Engineer Verification
    print_banner("Step 2: Engineer Investigation & Verification")
    print("Engineer completes diagnosis and confirms root cause and fix.")
    print("Saving engineer-confirmed resolution to Hindsight long-term memory...")

    actual_cause = "PostgreSQL connection pool exhausted due to leak in payment session handler."
    resolution = "Increased connection pool size to 50 and deployed session timeout fix."

    verify_resp = requests.post(
        f"{BASE_URL}/api/incidents/{inc_id_1}/verify",
        json={
            "actual_root_cause": actual_cause,
            "resolution": resolution,
            "verified": True
        },
        timeout=30
    )

    if verify_resp.status_code == 200:
        vdata = verify_resp.json()
        print(f"[SUCCESS] Incident verified!")
        print(f"Stored in Hindsight Memory: {vdata['stored_in_memory']}")
        print(f"Message: {vdata['message']}")
    else:
        print(f"[FAIL] Verification failed: {verify_resp.status_code} - {verify_resp.text}")
        return

    time.sleep(2)

    # 3. Second Incident: Learning from Hindsight Memory
    print_banner("Step 3: Recurring Incident - Memory Recall & Improved Recommendations")
    print("New similar logs arrive hours later from payments-service...")

    resp2 = requests.post(
        f"{BASE_URL}/api/incidents/analyze",
        json={"logs": SAMPLE_LOG_2, "service": "payments-service"},
        timeout=30
    )

    if resp2.status_code != 200:
        print(f"[FAIL] Analysis failed: {resp2.status_code} - {resp2.text}")
        return

    data2 = resp2.json()
    print(f"Incident ID Generated: {data2['incident_id']}")
    print(f"Assessed Severity:     {data2['severity']}")
    print(f"Historical Matches:    {len(data2['historical_matches'])} FOUND in Hindsight Memory!")

    if data2["historical_matches"]:
        print("\nRecalled Historical Verified Incident:")
        for h in data2["historical_matches"]:
            print(f"  * Ref ID:     {h.get('incident_id')}")
            print(f"  * Root Cause: {h.get('root_cause')}")
            print(f"  * Resolution: {h.get('resolution')}")

    print("\nAI Enhanced Possible Causes (Augmented with Memory):")
    for c in data2["possible_causes"]:
        print(f"  - [{c['confidence'].upper()}] {c['cause']}: {c['reason']}")

    print("\nAI Recommended Checks:")
    for chk in data2["recommended_checks"]:
        print(f"  -> {chk}")

    print_banner("Demo Complete - AI Agent Successfully Learned From Verified History!")


if __name__ == "__main__":
    run_demo()
