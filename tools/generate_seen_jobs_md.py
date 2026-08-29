#!/usr/bin/env python3
"""
Generate a human-readable Markdown summary of seen jobs.

Reads job_scraper/seen_jobs.json, filters to the last 14 days,
sorts by fit (high→medium→low) then first_seen descending,
and writes job_scraper/seen_jobs.md.

Title values are hyperlinked to each job posting's URL, and Company
values are hyperlinked to the company's LinkedIn profile or website
when a match is found in target_companies.md.

Usage:
    python3 tools/generate_seen_jobs_md.py
"""

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "job_scraper" / "seen_jobs.json"
MD_PATH = ROOT / "job_scraper" / "seen_jobs.md"
COMPANIES_PATH = ROOT / "target_companies.md"

FIT_ORDER = {"high": 0, "medium": 1, "low": 2}
CUTOFF = datetime.now(timezone.utc) - timedelta(days=14)


def load_seen() -> dict:
    if not JSON_PATH.exists():
        return {"seen": {}}
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def is_recent(first_seen: str) -> bool:
    """Check if a YYYY-MM-DD date string is within the last 14 days."""
    try:
        dt = datetime.strptime(first_seen, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt >= CUTOFF
    except (ValueError, TypeError):
        return False


def sort_key(item):
    """Sort by fit (high first), then first_seen descending (newest first)."""
    key, entry = item
    fit = entry.get("fit", "low").lower()
    fit_rank = FIT_ORDER.get(fit, 99)
    # Convert YYYY-MM-DD to integer for proper numeric negation (descending)
    date_str = entry.get("first_seen", "0000-00-00")
    try:
        date_int = int(date_str.replace("-", ""))
    except (ValueError, AttributeError):
        date_int = 0
    return (fit_rank, -date_int)


def load_company_links() -> dict:
    """Parse target_companies.md and return a mapping of normalized company name -> URL.

    Prefers LinkedIn profile URLs; falls back to Website URLs when LinkedIn
    is listed as "Search for ..." (i.e. not a real URL).
    """
    links: dict[str, str] = {}
    if not COMPANIES_PATH.exists():
        return links

    text = COMPANIES_PATH.read_text(encoding="utf-8")

    # Each company entry starts with a level-3 heading: ### Company Name
    heading_re = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
    # Capture the LinkedIn and Website field values within an entry
    linkedin_re = re.compile(r"^\s*-\s*\*\*LinkedIn:\*\*\s*(.+?)\s*$", re.MULTILINE)
    website_re = re.compile(r"^\s*-\s*\*\*Website:\*\*\s*(.+?)\s*$", re.MULTILINE)

    headings = list(heading_re.finditer(text))
    for idx, match in enumerate(headings):
        name = match.group(1).strip()
        start = match.end()
        end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
        block = text[start:end]

        url = None
        lm = linkedin_re.search(block)
        if lm:
            value = lm.group(1).strip()
            if value.startswith("http"):
                url = value
        if url is None:
            wm = website_re.search(block)
            if wm:
                value = wm.group(1).strip()
                if value.startswith("http"):
                    url = value
        if url:
            links[_normalize_company(name)] = url

    return links


def _normalize_company(name: str) -> str:
    """Normalize a company name for case-insensitive matching.

    Lowercases, strips common legal suffixes (OÜ, Inc, Ltd, etc.), and collapses
    whitespace so that 'Bolt' matches 'bolt' and '7p.marketing OÜ' matches
    '7p.marketing'.
    """
    s = name.strip().lower()
    # Strip common legal suffixes
    for suffix in (" oü", " ou", " inc.", " inc", " ltd.", " ltd", " llc", " oy", " oyj"):
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s


def _company_url(company: str, links: dict) -> str | None:
    """Return a URL for the given company name if present in the links map.

    Tries an exact normalized match first, then a starts-with fallback so
    that 'Bolt' (seen_jobs) matches 'bolt' (target_companies) and partial
    names like 'SEB Eesti' still match a 'SEB' entry if one existed.
    """
    norm = _normalize_company(company)
    if norm in links:
        return links[norm]
    # Fallback: target company name is a prefix of the seen-jobs company
    for key, url in links.items():
        if norm.startswith(key) or key.startswith(norm):
            return url
    return None


def format_table(entries: list, company_links: dict) -> str:
    """Build the Markdown table rows with hyperlinked Title and Company."""
    if not entries:
        return "_No jobs found in the last 14 days._\n"

    lines = [
        "| # | First Seen | Fit | Status | Score | Title | Company | Location |",
        "|---|------------|-----|--------|-------|-------|---------|----------|",
    ]

    for i, (key, entry) in enumerate(entries, start=1):
        first_seen = entry.get("first_seen", "?")
        fit = entry.get("fit", "?")
        status = entry.get("status", "?")
        title = entry.get("title", "?")
        company = entry.get("company", "?")
        rank_score = entry.get("rank_score")
        location = entry.get("location") or "—"

        # Resolve the job posting URL: prefer an explicit "url" field,
        # fall back to the JSON key when it is itself a URL.
        url = entry.get("url")
        if not url and isinstance(key, str) and key.startswith("http"):
            url = key

        # Format fit with bold for high
        fit_display = f"**{fit.upper()}**" if fit == "high" else fit.capitalize()

        # Format score if available
        score_display = f"{rank_score}" if rank_score is not None else "—"

        # Hyperlink the title to the job posting URL
        title_display = f"[{title}]({url})" if url else title

        # Hyperlink the company to its LinkedIn/website when known
        company_url = _company_url(company, company_links)
        company_display = f"[{company}]({company_url})" if company_url else company

        lines.append(
            f"| {i} | {first_seen} | {fit_display} | {status} | {score_display} | {title_display} | {company_display} | {location} |"
        )

    return "\n".join(lines) + "\n"


def generate() -> str:
    data = load_seen()
    seen = data.get("seen", {})

    # Load company LinkedIn/website links for Company-column hyperlinks
    company_links = load_company_links()

    # Filter to recent entries
    recent = [(k, v) for k, v in seen.items() if is_recent(v.get("first_seen", ""))]

    # Sort: fit (high→medium→low), then first_seen descending
    recent.sort(key=sort_key)

    # Count by fit
    high = sum(1 for _, v in recent if v.get("fit") == "high")
    medium = sum(1 for _, v in recent if v.get("fit") == "medium")
    low = sum(1 for _, v in recent if v.get("fit") == "low")

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Seen Jobs — Last 14 Days",
        f"",
        f"_Generated: {now_str}_",
        f"",
        f"**{len(recent)} jobs** ({high} high, {medium} medium, {low} low match).",
        f"",
    ]

    lines.append(format_table(recent, company_links))

    return "\n".join(lines)


def main():
    md_content = generate()
    MD_PATH.write_text(md_content, encoding="utf-8")
    count = len(json.loads(JSON_PATH.read_text(encoding="utf-8")).get("seen", {}))
    print(f"Written {MD_PATH} ({count} total entries, {md_content.count('|') // 8 - 2} recent)")


if __name__ == "__main__":
    main()