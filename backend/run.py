import uvicorn
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    print(f"Starting ShareVal Valuation Service on http://{host}:{port} ...")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=reload)
