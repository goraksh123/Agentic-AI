# config.py
# Configuration for ERP Documentation Agent

import os
from dotenv import load_dotenv

load_dotenv()

# ── ANTHROPIC API ──────────────────────────
ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY",
    "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"
)
MODEL             = "claude-sonnet-4-20250514"
MAX_TOKENS        = 8000

# ── YOUR ERP PATH ──────────────────────────
# Change this to your Font Accounting path!
ERP_PATH = r"/Users/gorakshnaik/Documents/LocalRepo/SSLEKHA/erp_sslekha1-prod/erp_sslekha/sslekha"  # Windows example
# OR Linux/Mac:
# ERP_PATH = "/var/www/html/fontaccounting"

# ── DATABASE CONFIG ────────────────────────
DB_CONFIG = {
    "host"    : "139.59.11.188",
    "user"    : "lekhaa5_fa",
    "password": "b-d-p5%~F(yQ!cBkH;U4T",           # your DB password
    "database": "multibranch_test",  # your DB name
    "port"    : 3306
}

# ── WHAT TO SCAN ───────────────────────────
SCAN_EXTENSIONS = [
    ".php",
    ".html",
    ".js",
    ".css",
    ".sql"
]

# ── FOLDERS TO SKIP ────────────────────────
SKIP_FOLDERS = [
    "vendor",
    "node_modules",
    ".git",
    "cache",
    "temp",
    "tmp",
    "logs"
]

# ── OUTPUT PATH ────────────────────────────
OUTPUT_PATH = "./output"

# ── MAX FILE SIZE TO READ (bytes) ──────────
MAX_FILE_SIZE = 50000   # 50KB per file