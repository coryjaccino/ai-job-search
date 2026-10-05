#!/usr/bin/env python3
"""
Generate a human-readable Markdown summary of seen jobs.

Reads job_scraper/seen_jobs.json and groups postings by publication age.
Archive candidates are hidden unless --include-archive is supplied.
No database records are modified.

Title values are hyperlinked to each job posting's URL, and Company
values are hyperlinked to the company's LinkedIn profile or website
when a match is found in target_companies.md.

Usage:
    python3 tools/generate_seen_jobs_md.py
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .job_freshness import freshness, sort_key
else:
    from job_freshness import freshness, sort_key

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "job_scraper" / "seen_jobs.json"
MD_PATH = ROOT / "job_scraper" / "seen_jobs.md"
COMPANIES_PATH = ROOT / "target_companies.md"



def load_seen() -> dict:
    if not JSON_PATH.exists():
        return {"seen": {}}
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


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


def format_table(entries: list, company_links: dict, today=None) -> str:
    """Build the Markdown table rows with hyperlinked Title and Company."""
    if not entries:
        return "_No postings in this section._\n"

    lines = [
        "| # | Published | Age | Date confidence | First seen | Fit | Workflow | Score | Availability | Last verified open | Title | Company | Location |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for i, (key, entry) in enumerate(entries, start=1):
        first_seen = entry.get("first_seen", "?")
        fit = entry.get("fit", "?")
        status = entry.get("status", "?")
        title = str(entry.get("title", "?")).replace('|', '\\|').replace('\n', ' ')
        company = str(entry.get("company", "?")).replace('|', '\\|').replace('\n', ' ')
        rank_score = entry.get("evaluation_score", entry.get("rank_score"))
        location = str(entry.get("location") or "—").replace('|', '\\|').replace('\n', ' ')
        info = freshness(entry, today)
        availability = entry.get('availability', 'unverified')
        verified = entry.get('last_verified_open', '—')

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
            f"| {i} | {info['published_date'] or '—'} | {str(info['age_days']) + 'd' if info['age_days'] is not None else '—'} | {info['confidence']} | {first_seen} | {fit_display} | {status} | {score_display} | {availability} | {verified} | {title_display} | {company_display} | {location} |"
        )

    return "\n".join(lines) + "\n"


def generate(include_archive=False, today=None) -> str:
    data = load_seen()
    seen = data.get("seen", {})

    # Load company LinkedIn/website links for Company-column hyperlinks
    company_links = load_company_links()

    active = [(k, v) for k, v in seen.items() if v.get('status') not in ('expired', 'applied', 'skipped') and v.get('availability') != 'closed']
    groups = {name: [] for name in ('Fresh', 'Current', 'Aging', 'Older', 'Archive candidate', 'Undated')}
    for item in active:
        groups[freshness(item[1], today)['band']].append(item)
    for entries in groups.values():
        entries.sort(key=lambda item: sort_key(item, today))

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Job Opportunities — Posting Freshness",
        f"",
        f"_Generated: {now_str}_",
        f"",
        f"**{len(active)} active candidates** out of {len(seen)} stored records. Workflow and availability are independent of age.",
        "Default shortlist: Fresh (0–7d) + Current (8–14d). Older and undated sections are review queues, not confirmed-open shortlists.",
        "Dates marked source-reported/uncertain may be aggregator refresh dates. Collection and verification do not reset publication age.",
        "Numeric scores take precedence; unscored entries use high/medium/low fallback priority. Evaluation scores supersede triage scores. Deadline urgency, then age, break ties.",
        f"",
    ]

    for name, entries in groups.items():
        if name == 'Archive candidate' and not include_archive:
            lines.append(f"\n_Archive candidates hidden: {len(entries)}. Use --include-archive to display; records are retained._\n")
            continue
        lines.append(f"\n## {name} ({len(entries)})\n")
        lines.append(format_table(entries, company_links, today))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-archive', action='store_true')
    args = parser.parse_args()
    md_content = generate(args.include_archive)
    MD_PATH.write_text(md_content, encoding="utf-8")
    count = len(json.loads(JSON_PATH.read_text(encoding="utf-8")).get("seen", {}))
    print(f"Written {MD_PATH} ({count} stored entries; grouped by publication age)")


if __name__ == "__main__":
    main()