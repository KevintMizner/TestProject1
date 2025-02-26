import os
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'server': 'sql-wmsag',
    'database': 'AD_Analysis',
    'username': 'api_interface',
    'password': 'Z@7824_aPi',
}

# Logging configuration
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "yms_del.log"

# File paths
DOWNLOAD_DIR = Path(__file__).resolve().parent / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
