import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import csv
import datetime
from config import TRACKER_FILE

TRACKER_HEADERS = [
    "date_added", "company", "title", "location", "url",
    "status", "cover_letter_file", "resume_file", "notes"
]

VALID_STATUSES = ["To Apply", "Applied", "Interview", "Offer", "Rejected", "Ghosted"]


# ─── Init ─────────────────────────────────────────
def init_tracker():
    """Create the CSV file with headers if it doesn't exist."""
    path = Path(TRACKER_FILE)
    if not path.exists():
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=TRACKER_HEADERS)
            writer.writeheader()


# ─── Add ──────────────────────────────────────────
def add_application(job: dict, cover_letter_file: str = "", resume_file: str = ""):
    """Add a new job application to the tracker."""
    init_tracker()
    row = {
        "date_added":        datetime.date.today().isoformat(),
        "company":           job.get("company", ""),
        "title":             job.get("title", ""),
        "location":          job.get("location", ""),
        "url":               job.get("url", ""),
        "status":            "To Apply",
        "cover_letter_file": cover_letter_file,
        "resume_file":       resume_file,
        "notes":             "",
    }
    with open(TRACKER_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_HEADERS)
        writer.writerow(row)


# ─── View ─────────────────────────────────────────
def get_all_applications() -> list[dict]:
    """Return all applications as a list of dicts."""
    init_tracker()
    with open(TRACKER_FILE, newline="") as f:
        return list(csv.DictReader(f))


# ─── Update ───────────────────────────────────────
def update_status(company: str, title: str, new_status: str):
    """Update the status of a tracked application."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Choose from: {VALID_STATUSES}")

    rows = get_all_applications()
    updated = False

    for row in rows:
        if row["company"].lower() == company.lower() and row["title"].lower() == title.lower():
            row["status"] = new_status
            updated = True

    if not updated:
        raise LookupError(f"No application found for '{company}' / '{title}'")

    with open(TRACKER_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

# Test
# add_application({"company": "Stripe", "title": "Engineer", "location": "Remote", "url": "https://stripe.com"})
# print(get_all_applications())