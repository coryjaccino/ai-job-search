#!/usr/bin/env python3
"""
Fetches LinkedIn job posting details with authenticated access, including the
"People you can reach out to" contacts section.

Usage:
    python3 tools/linkedin_auth_fetch.py <job-id-or-url> [--profile-dir <path>]

Outputs JSON to stdout with JobDetail + contacts array.
Contacts include: name, title (position), profileUrl, company, companyUrl, relationship.

Requires:
    - Playwright installed (pip install playwright && playwright install chromium)
    - The user's Chrome/Chromium profile directory path (for authenticated session)
    - The user to be logged into LinkedIn in that browser profile

Anti-ban considerations:
    - Reuses existing browser session (no new login needed)
    - Adds random delays between actions
    - Uses human-like navigation patterns
"""

import argparse
import json
import re
import sys
import time
import random
from pathlib import Path

from playwright.sync_api import sync_playwright


def normalize_job_id(input_str: str) -> str | None:
    """Extract numeric job ID from a LinkedIn job URL or URN."""
    # Try urn:li:jobPosting:1234567890
    urn = re.search(r"urn:li:jobPosting:(\d+)", input_str)
    if urn:
        return urn[1]
    # Try /jobs/view/-1234567890/
    url = re.search(r"/jobs/view/-(\d{6,})/", input_str)
    if url:
        return url[1]
    # Try bare numeric ID
    bare = re.match(r"^(\d{6,})$", input_str.strip())
    if bare:
        return bare[1]
    return None


def extract_contacts(html: str) -> list[dict]:
    """
    Parse the 'People you can reach out to' section from a LinkedIn job posting page.

    LinkedIn renders this section in a div with class containing
    'jobs-peopleAlsoViewed' or 'artdeco-card' with related contacts.
    The actual contacts appear in a section with heading text like
    "People who work at <company>" or "People you can reach out to".

    Returns list of dicts: {name, title, profileUrl, company, companyUrl, relationship}
    """
    contacts = []

    # Pattern 1: The contacts card typically has a header and list of people cards
    # Each person card contains:
    # - <a href="/in/username"> with the person's name
    # - Company info (may be in a subtitle)
    # - Relationship indicator (e.g., "School alum", "2nd connection")

    # Look for the contacts section by finding cards with peopleAlsoViewed or similar
    # The HTML structure varies, so we use multiple patterns

    # Pattern: Find all person cards within the job details page
    # Each card typically has data-view-name="identity-card" or similar
    # and contains <a> tags to /in/ profiles

    # Extract individual profile links and associated text
    # Structure is typically:
    # <div class="...peopleAlsoViewed...">
    #   <h2>People you can reach out to</h2>
    #   <ul>
    #     <li>
    #       <a href="/in/username" class="...">
    #         <img src="..." />
    #         <span class="...">Name</span>
    #         <span class="...">Title at Company</span>
    #       </a>
    #       <span class="...relationship info...">School alum from ...</span>
    #     </li>
    #   </ul>
    # </div>

    # More robust: find all /in/ links that appear after the job description area
    # and are associated with contact cards

    # Try to find the contacts section by its heading
    contacts_section_patterns = [
        r"People\s+you\s+can\s+reach\s+out\s+to",
        r"People\s+who\s+work\s+at",
        r"Related\s+contacts",
    ]

    has_contacts_section = any(
        re.search(p, html, re.IGNORECASE) for p in contacts_section_patterns
    )

    if not has_contacts_section:
        return contacts

    # Find all LinkedIn profile links with surrounding context
    # The contact cards have a specific structure with profile links
    profile_link_pattern = re.compile(
        r'<a\s+[^>]*href="(/in/[^"]+)"[^>]*class="[^"]*mn-internal-link[^"]*"[^>]*>([\s\S]*?)</a>',
        re.MULTILINE,
    )

    # Alternative: match any /in/ link that's in a card-like structure
    all_profile_links = re.findall(
        r'href="(/in/[^\?]+)"[^>]*>(\s*<[^>]*>\s*)?([^<]*)', html
    )

    # Filter to only the contacts section profiles
    # We look for profile links that appear near relationship indicators
    relationship_indicators = [
        "School alum",
        "2nd",
        "2nd degree",
        "3rd",
        "3rd degree",
        "Former colleague",
        "Co-worker",
        "connection",
    ]

    # Parse each profile link with its surrounding HTML context
    for profile_url, _tag_wrapper, name in all_profile_links:
        # Clean up the name
        name = re.sub(r"<[^>]+>", "", name).strip()
        if not name or len(name) < 2:
            continue

        # Skip if this looks like a company page or content link
        if "/company/" in profile_url or "/pulse/" in profile_url or "/school/" in profile_url:
            continue

        # Get the surrounding context (500 chars around this link)
        link_pos = html.find(f'href="{profile_url}"')
        if link_pos == -1:
            continue

        context_start = max(0, link_pos - 800)
        context_end = min(len(html), link_pos + 800)
        context = html[context_start:context_end]

        # Check if there's a relationship indicator in the context
        has_relationship = any(
            re.search(ind, context, re.IGNORECASE) for ind in relationship_indicators
        )

        if not has_relationship:
            continue

        # Extract relationship text
        relationship = None
        for ind in relationship_indicators:
            rel_match = re.search(r"(" + ind + r"[^<]*)", context, re.IGNORECASE)
            if rel_match:
                relationship = rel_match[1].strip()
                break

        # Extract title/position and company info from the subtitle text
        # LinkedIn typically shows: "GTM Leader at Legora" or similar patterns
        # The structure is often: <span>Title</span> at <a href="/company/...">Company</a>
        # Or inline text like "Senior Software Engineer at Google"
        title = None
        company = None
        company_url = None

        # Pattern 1: Look for "<title> at <company>" where company is a link
        title_at_company = re.search(
            r'>([^<]+?)\s+at\s+<a\s+[^>]*href=\"(/company/[^\"]+)\"[^>]*>([^<]+)',
            context,
        )
        if title_at_company:
            title = title_at_company[1].strip()
            company_url = f"https://www.linkedin.com{title_at_company[2]}"
            company = title_at_company[3].strip()

        # Pattern 2: Look for subtitle span with "Title at Company" as plain text
        if not title:
            subtitle_text = re.search(
                r'class="[^"]*subtitle[^"]*"[^>]*>([^<]+)', context, re.IGNORECASE
            )
            if subtitle_text:
                subtitle = subtitle_text[1].strip()
                # Try to split "Title at Company"
                at_match = re.match(r"(.+?)\s+at\s+(.+)", subtitle)
                if at_match:
                    title = at_match[1].strip()
                    company = at_match[2].strip()

        # Pattern 3: Look for any text before "at CompanyLink" pattern
        if not company:
            at_company = re.search(
                r'at\s+<a\s+[^>]*href=\"(/company/[^\"]+)\"[^>]*>([^<]+)', context
            )
            if at_company:
                company_url = f"https://www.linkedin.com{at_company[1]}"
                company = at_company[2].strip()
                # Try to find title text before "at"
                before_at = context[:context.find(at_company.group(0))].strip()
                title_match = re.search(r'>([^<]+)<$', before_at)
                if title_match:
                    title = title_match[1].strip()

        # Pattern 4: If no "at company" pattern, look for any company link in the card
        if not company:
            company_link = re.search(
                r'href="(/company/[^\?]+)"[^>]*>(\s*<[^>]*>\s*)?([^<]*)', context
            )
            if company_link:
                company_url = f"https://www.linkedin.com{company_link[1]}"
                company = company_link[3].strip() if company_link[3].strip() else None

        # Build full profile URL
        full_profile_url = f"https://www.linkedin.com{profile_url}"

        contacts.append(
            {
                "name": name,
                "title": title,
                "profileUrl": full_profile_url,
                "company": company,
                "companyUrl": company_url,
                "relationship": relationship,
            }
        )

    # Deduplicate by profile URL
    seen_urls = set()
    unique_contacts = []
    for c in contacts:
        if c["profileUrl"] not in seen_urls:
            seen_urls.add(c["profileUrl"])
            unique_contacts.append(c)

    return unique_contacts


def fetch_job_detail(job_id: str, profile_dir: str | None = None) -> dict:
    """
    Fetch a LinkedIn job posting using Playwright with the user's browser profile.
    Returns a dict with job details + contacts.
    """
    job_url = f"https://www.linkedin.com/jobs/view/-{job_id}/"

    result = {"error": None, "job": None, "contacts": []}

    with sync_playwright() as pw:
        browser = None
        try:
            if profile_dir:
                # Launch Chrome with the user's existing profile for authentication
                browser = pw.chromium.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=True,
                    slow_mo=random.randint(100, 300),  # Human-like delays
                    viewport={"width": 1280, "height": 900},
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                )
            else:
                # Fallback: launch without profile (may not have contacts data)
                browser = pw.chromium.launch(
                    headless=True,
                    slow_mo=random.randint(100, 300),
                )

            page = browser.new_page()

            # Add random delay before navigation (anti-bot)
            time.sleep(random.uniform(1, 3))

            page.goto(job_url, wait_until="networkidle", timeout=30000)

            # Wait for the page to fully render with human-like delay
            time.sleep(random.uniform(2, 5))

            # Scroll down to trigger lazy-loaded content (anti-bot + ensure contacts load)
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(random.uniform(1, 2))
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(random.uniform(1, 2))

            # Get the full page HTML
            html = page.content()

            # Parse job details (reuse patterns from helpers.ts)
            job = parse_job_detail_from_html(html, job_id)

            # Extract contacts
            contacts = extract_contacts(html)

            result["job"] = job
            result["contacts"] = contacts

        except Exception as e:
            result["error"] = str(e)
        finally:
            if browser:
                browser.close()


def parse_job_detail_from_html(html: str, job_id: str) -> dict:
    """Parse job details from HTML content."""
    job = {
        "id": job_id,
        "title": None,
        "company": None,
        "companyUrl": None,
        "location": None,
        "url": f"https://www.linkedin.com/jobs/view/-{job_id}/",
        "description": None,
        "seniority": None,
        "employmentType": None,
        "jobFunction": None,
        "industries": None,
        "applyUrl": None,
    }

    # Title
    title_match = re.search(
        r'class="(?:top-card-layout__title|topcard__title)[^"]*"[^>]*>([\s\S]*?)<\/h[12]>',
        html,
    )
    if title_match:
        job["title"] = clean_html(title_match[1])

    # Company
    org_match = re.search(
        r'class="topcard__org-name-link[^"]*"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>',
        html,
    )
    if org_match:
        job["companyUrl"] = decode_html_entities(org_match[1]).split("?")[0]
        job["company"] = clean_html(org_match[2])

    # Location
    loc_match = re.search(
        r'class="topcard__flavor topcard__flavor--bullet"[^>]*>([\s\S]*?)<\/span>',
        html,
    )
    if loc_match:
        job["location"] = clean_html(loc_match[1])

    # Description
    desc_match = re.search(
        r'class="show-more-less-html__markup[^"]*"[^>]*>([\s\S]*?)</div>',
        html,
    )
    if not desc_match:
        desc_match = re.search(
            r'class="description__text[^"]*"[^>]*>([\s\S]*?)</div>', html
        )
    if desc_match:
        desc_html = desc_match[1]
        desc_html = re.sub(r"<\s*br\s*/?>", "\n", desc_html, flags=re.IGNORECASE)
        desc_html = re.sub(
            r"</(p|li|ul|ol|div|h\d)>", "\n", desc_html, flags=re.IGNORECASE
        )
        job["description"] = clean_html(desc_html)

    # Job criteria
    criteria = {}
    item_re = re.compile(
        r'class="description__job-criteria-subheader"[^>]*>([\s\S]*?)<\/h3>'
        r'[\s\S]*?class="description__job-criteria-text[^"]*"[^>]*>([\s\S]*?)<\/span>',
        re.IGNORECASE,
    )
    for m in item_re.finditer(html):
        key = clean_html(m[1]).lower()
        criteria[key] = clean_html(m[2])

    job["seniority"] = criteria.get("seniority level")
    job["employmentType"] = criteria.get("employment type")
    job["jobFunction"] = criteria.get("job function")
    job["industries"] = criteria.get("industries")

    # Apply URL
    apply_match = re.search(
        r'class="topcard__link[^"]*"[^>]*href="([^"]+)"', html, re.IGNORECASE
    )
    if apply_match:
        job["applyUrl"] = decode_html_entities(apply_match[1]).split("?")[0]

    return job


def clean_html(html: str) -> str | None:
    """Strip tags and decode HTML entities."""
    if not html:
        return None
    text = re.sub(r"<[^>]+>", " ", html)
    text = decode_html_entities(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else None


def decode_html_entities(text: str) -> str:
    """Decode HTML entities."""
    import html

    return html.unescape(text)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch LinkedIn job details with contacts (authenticated)"
    )
    parser.add_argument(
        "job_id",
        help="Job ID, URL, or URN (e.g., 4422756894 or https://www.linkedin.com/jobs/view/-4422756894/)",
    )
    parser.add_argument(
        "--profile-dir",
        default=None,
        help="Path to Chrome/Chromium user data directory for authenticated session",
    )
    parser.add_argument(
        "--output",
        choices=["json", "plain"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    # Normalize the job ID
    job_id = normalize_job_id(args.job_id)
    if not job_id:
        print(
            json.dumps({"error": f"Could not parse job ID from: {args.job_id}"}),
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.profile_dir:
        # Try common Chrome profile locations
        home = Path.home()
        possible_profiles = [
            home / "Library/Application Support/Google/Chrome",  # macOS default Chrome
            home / "Library/Application Support/Chromium",  # macOS Chromium
            home / ".config/google-chrome",  # Linux Chrome
            home / ".config/chromium",  # Linux Chromium
        ]
        for p in possible_profiles:
            if p.exists():
                args.profile_dir = str(p)
                break

    if not args.profile_dir:
        print(
            json.dumps(
                {
                    "error": (
                        "No Chrome profile directory found. "
                        "Provide --profile-dir path to your Chrome user data directory. "
                        "On macOS, this is typically: ~/Library/Application Support/Google/Chrome"
                    )
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    # Close any running Chrome instances message (they'll conflict with profile reuse)
    result = fetch_job_detail(job_id, args.profile_dir)

    if result["error"]:
        print(json.dumps({"error": result["error"]}), file=sys.stderr)
        sys.exit(1)

    if args.output == "json":
        output = {
            "job": result["job"],
            "contacts": result["contacts"],
            "contactsCount": len(result["contacts"]),
        }
        print(json.dumps(output, indent=2))
    else:
        job = result["job"] or {}
        lines = [
            job.get("title", "(untitled)"),
            f"{job.get('company', '—')} · {job.get('location', '—')}",
            "",
        ]
        if job.get("seniority"):
            lines.append(f"Seniority: {job['seniority']}")
        if job.get("employmentType"):
            lines.append(f"Employment: {job['employmentType']}")
        if job.get("jobFunction"):
            lines.append(f"Function: {job['jobFunction']}")
        if job.get("industries"):
            lines.append(f"Industries: {job['industries']}")
        lines.append("")
        lines.append(job.get("description", "(no description)") or "(no description)")
        lines.append("")
        lines.append(f"URL: {job.get('url', '')}")
        if job.get("applyUrl"):
            lines.append(f"Apply: {job['applyUrl']}")

        # Contacts section
        if result["contacts"]:
            lines.append("")
            lines.append(f"Contacts ({len(result['contacts'])} people you can reach out to):")
            for i, c in enumerate(result["contacts"], 1):
                lines.append(f"  {i}. {c.get('name', 'Unknown')}")
                if c.get("title"):
                    lines.append(f"     Title: {c['title']}")
                if c.get("company"):
                    lines.append(f"     Company: {c['company']}")
                if c.get("companyUrl"):
                    lines.append(f"     Company URL: {c['companyUrl']}")
                if c.get("relationship"):
                    lines.append(f"     Relationship: {c['relationship']}")
                if c.get("profileUrl"):
                    lines.append(f"     Profile: {c['profileUrl']}")

        print("\n".join(lines))


if __name__ == "__main__":
    main()