import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")
BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io"
)

BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "incident-response-memory"
)


def setup_memory_bank():

    if not API_KEY:
        raise ValueError("HINDSIGHT_API_KEY is missing")

    client = Hindsight(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    try:

        bank = client.create_bank(
            bank_id=BANK_ID,
            name="AI Incident Response Agent",
            background=(
                "This memory bank stores verified historical "
                "server and application incidents, their root "
                "causes, diagnostic evidence, and successful "
                "resolutions. Only engineer-verified incidents "
                "should be stored."
            )
        )

        print("Memory bank created successfully!")
        print("Bank ID:", bank.bank_id)

    finally:
        client.close()


if __name__ == "__main__":
    setup_memory_bank()