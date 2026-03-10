import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import requests
import feedparser
import mechanicalsoup
from config import JOB_FEEDS


# ─── Helpers ──────────────────────────────────────
def _deduplicate(jobs: list[dict]) -> list[dict]:
    """Remove duplicate jobs by URL, silently."""
    seen, unique = set(), []
    for job in jobs:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)
    return unique


def _normalize(company="", title="", location="Remote", url="", source="") -> dict:
    """Return a consistent job dict structure."""
    return {
        "company":  company,
        "title":    title,
        "location": location,
        "url":      url,
        "source":   source,
    }


# ─── RemoteOK ─────────────────────────────────────
def scrape_remoteok(keywords: list[str]) -> list[dict]:
    """Scrape RemoteOK JSON feed."""
    try:
        resp = requests.get(
            JOB_FEEDS["remoteok"],
            timeout=10,
            headers={"User-Agent": "JobSearchAutomator/1.0"}
        )
        resp.raise_for_status()
        jobs = []
        for job in resp.json():
            if not isinstance(job, dict) or "position" not in job:
                continue
            title = job.get("position", "").lower()
            tags  = " ".join(job.get("tags", [])).lower()
            if any(kw.lower() in title or kw.lower() in tags for kw in keywords):
                jobs.append(_normalize(
                    company  = job.get("company", ""),
                    title    = job.get("position", ""),
                    location = "Remote",
                    url      = job.get("url", ""),
                    source   = "RemoteOK",
                ))
        return jobs
    except Exception as e:
        print(f"[RemoteOK] Failed: {e}")
        return []


# ─── WeWorkRemotely ───────────────────────────────
def scrape_wwr(keywords: list[str]) -> list[dict]:
    """Scrape WeWorkRemotely RSS feeds."""
    jobs = []
    for key in ["wwr_engineering", "wwr_design"]:
        try:
            feed = feedparser.parse(JOB_FEEDS[key])
            for entry in feed.entries:
                title   = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()
                if any(kw.lower() in title or kw.lower() in summary for kw in keywords):
                    jobs.append(_normalize(
                        company  = entry.get("author", "Unknown"),
                        title    = entry.get("title", ""),
                        location = "Remote",
                        url      = entry.get("link", ""),
                        source   = "WeWorkRemotely",
                    ))
        except Exception as e:
            print(f"[WWR:{key}] Failed: {e}")
    return jobs


# ─── LinkedIn ─────────────────────────────────────
def scrape_linkedin(keywords: list[str]) -> list[dict]:
    """Scrape LinkedIn jobs using MechanicalSoup."""
    jobs = []
    try:
        browser = mechanicalsoup.StatefulBrowser()
        query   = "%20".join(keywords)
        url     = f"https://www.linkedin.com/jobs/search/?keywords={query}"
        browser.open(url)
        page = browser.page

        for card in page.select("div.job-search-card"):
            title   = card.select_one("h3.base-search-card__title")
            company = card.select_one("h4.base-search-card__subtitle")
            link    = card.select_one("a.base-card__full-link")
            if title and company and link:
                jobs.append(_normalize(
                    company  = company.get_text(strip=True),
                    title    = title.get_text(strip=True),
                    location = "See listing",
                    url      = link.get("href", ""),
                    source   = "LinkedIn",
                ))
    except Exception as e:
        print(f"[LinkedIn] Failed: {e}")
    return jobs


# ─── Indeed ───────────────────────────────────────
def scrape_indeed(keywords: list[str]) -> list[dict]:
    """Scrape Indeed jobs using MechanicalSoup."""
    jobs = []
    try:
        browser = mechanicalsoup.StatefulBrowser()
        query   = "+".join(keywords)
        url     = f"https://www.indeed.com/jobs?q={query}"
        browser.open(url)
        page = browser.page

        for card in page.select("div.job_seen_beacon"):
            title   = card.select_one("h2.jobTitle")
            company = card.select_one("span.companyName")
            link    = card.select_one("a")
            if title and company and link:
                jobs.append(_normalize(
                    company  = company.get_text(strip=True),
                    title    = title.get_text(strip=True),
                    location = "See listing",
                    url      = "https://indeed.com" + link.get("href", ""),
                    source   = "Indeed",
                ))
    except Exception as e:
        print(f"[Indeed] Failed: {e}")
    return jobs


# ─── Main Entry ───────────────────────────────────
def find_jobs(keywords: list[str], limit: int = 10) -> list[dict]:
    """Aggregate jobs from all sources, deduplicate, and return up to limit."""
    all_jobs = []
    all_jobs += scrape_remoteok(keywords)
    all_jobs += scrape_wwr(keywords)
    all_jobs += scrape_linkedin(keywords)
    all_jobs += scrape_indeed(keywords)

    unique = _deduplicate(all_jobs)
    return unique[:limit]


# Test
# if __name__ == "__main__":
#     results = find_jobs(["python", "software engineer"], limit=5)
#     for job in results:
#         print(job)