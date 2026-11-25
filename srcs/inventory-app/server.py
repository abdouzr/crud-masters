import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("INVENTORY_HOST", "0.0.0.0")
    port = int(os.environ.get("INVENTORY_PORT", "8080"))
    app.run(host=host, port=port)
