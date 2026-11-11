from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
FRONTEND_DIR = BASE_DIR / "frontend"

APP_NAME = "ShareVal - Stock & Option Fair Valuation Service"
API_V1_PREFIX = "/api/v1"
DEFAULT_DATA_SOURCE = os.getenv("DEFAULT_DATA_SOURCE", "mock")  # 'mock' or 'yahoo'
DEFAULT_RISK_FREE_RATE = float(os.getenv("DEFAULT_RISK_FREE_RATE", "0.045"))  # 4.5%
DEFAULT_BOND_YIELD = float(os.getenv("DEFAULT_BOND_YIELD", "0.045"))  # 4.5% AAA yield
