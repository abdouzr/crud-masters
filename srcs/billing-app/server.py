from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app import run_billing_service

if __name__ == "__main__":
    run_billing_service()
