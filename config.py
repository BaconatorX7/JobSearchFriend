from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# ─── API ───────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise EnvironmentError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000

# ─── Job Sources ───────────────────────────────────
JOB_FEEDS = {
    "remoteok": "https://remoteok.com/remote-jobs.json",
    "wwr_engineering": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "wwr_design": "https://weworkremotely.com/categories/remote-design-jobs.rss",
}

# ─── Paths ─────────────────────────────────────────
TRACKER_FILE = "applications.csv"
OUTPUT_DIR   = "job_applications"

# ─── Defaults ──────────────────────────────────────
DEFAULT_JOB_LIMIT = 10