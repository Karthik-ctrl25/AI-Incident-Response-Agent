from app.services.hindsight_service import (
    HindsightMemoryService
)


def main():

    service = HindsightMemoryService()

    try:

        # --------------------------------
        # TEST 1: STORE VERIFIED INCIDENT
        # --------------------------------

        print("\nTEST 1: Storing Incident")

        result = service.store_verified_incident(
            incident_id="INC-001",

            service_name="payment-service",

            severity="high",

            logs="""
            psycopg2.OperationalError:
            could not connect to server
            Connection timed out
            """,

            root_cause=(
                "PostgreSQL reached its maximum "
                "connection limit due to excessive "
                "connections from payment-service."
            ),

            resolution=(
                "Increased connection pool configuration "
                "and implemented connection reuse."
            ),

            verified=True
        )

        print(result)

        # --------------------------------
        # TEST 2: RECALL SIMILAR INCIDENT
        # --------------------------------

        print("\nTEST 2: Similar Incident Recall")

        result = service.recall_similar_incidents(

            logs="""
            psycopg2.OperationalError:
            database connection timeout
            remaining connection slots are reserved
            """,

            service_name="payment-service"
        )

        print("Retrieved incidents:", result["count"])

        for incident in result["incidents"]:

            print("\nHistorical Memory:")
            print(incident["content"])

        # --------------------------------
        # TEST 3: UNRELATED INCIDENT
        # --------------------------------

        print("\nTEST 3: Unrelated Incident Recall")

        result = service.recall_similar_incidents(

            logs="""
            MemoryError:
            Unable to allocate memory
            Java heap space exceeded
            """,

            service_name="analytics-service"
        )

        print("Retrieved incidents:", result["count"])

        for incident in result["incidents"]:

            print("\nHistorical Memory:")
            print(incident["content"])

    finally:

        service.close()


if __name__ == "__main__":
    main()