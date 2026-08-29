#!/usr/bin/env python3
"""
Filter job_scraper/seen_jobs.json based on search-queries.md and job_scraper/preferences.json.

Removes postings that:
1. Match excluded title keywords from job_scraper/preferences.json.
2. Are from excluded companies from job_scraper/preferences.json.
3. Are from excluded regions or job board domains from job_scraper/preferences.json.
4. Are in the job feedback log from job_scraper/preferences.json.
5. Violate the Language Filter in search-queries.md (English/Spanish only).
6. Violate the Location Focus in search-queries.md (US remote, Estonia, or EU/Global remote).
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "job_scraper" / "seen_jobs.json"
QUERIES_PATH = ROOT / ".claude" / "skills" / "job-scraper" / "search-queries.md"
PREFERENCES_PATH = ROOT / "job_scraper" / "preferences.json"

# Languages to exclude (from search-queries.md)
EXCLUDED_LANGUAGES = [
    "Arabic", "Bulgarian", "Dutch", "Finnish", "French", "German", 
    "Greek", "Hungarian", "Polish", "Romanian", "Russian", "Ukrainian"
]

def load_json(path: Path) -> dict:
    if not path.exists():
        return {"seen": {}}
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _normalized_string_list(data: dict, key: str) -> list[str]:
    """Return a non-empty, case-normalized list or raise a helpful schema error."""
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{PREFERENCES_PATH}: {key} must be a list of non-empty strings")
    return [item.strip().lower() for item in value]


def parse_preferences(path: Path = PREFERENCES_PATH) -> dict:
    """Load and validate the dependency-free JSON preferences configuration."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Missing preferences configuration: {path}. Create it from job_scraper/preferences.json."
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON ({exc.msg}, line {exc.lineno}, column {exc.colno})") from exc

    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"{path}: schema_version must be the number 1")

    feedback = data.get("job_feedback")
    if not isinstance(feedback, list) or not all(isinstance(item, dict) for item in feedback):
        raise ValueError(f"{path}: job_feedback must be a list of objects")

    feedback_urls = []
    for index, item in enumerate(feedback):
        if not all(isinstance(item.get(field), str) and item[field].strip() for field in ("date", "company", "title", "issue")):
            raise ValueError(f"{path}: job_feedback[{index}] requires non-empty date, company, title, and issue strings")
        url = item.get("url")
        if url is not None:
            if not isinstance(url, str) or not url.startswith(("https://", "http://")):
                raise ValueError(f"{path}: job_feedback[{index}].url must be an http(s) URL when present")
            feedback_urls.append(url)

    return {
        "titles": _normalized_string_list(data, "excluded_title_keywords"),
        "boards": _normalized_string_list(data, "excluded_regions_and_job_boards"),
        "companies": _normalized_string_list(data, "excluded_companies"),
        "feedback_urls": feedback_urls,
    }

def is_excluded_by_language(title: str, entry: dict) -> bool:
    """Check if the job violates the English/Spanish language filter."""
    # Check for Cyrillic or other non-Latin characters in title (indicating non-English/Spanish audience)
    # Allows common Latin-1/accents for Spanish/English
    if re.search(r'[\u0400-\u04FF]', title): # Simple Cyrillic check
        return True
    
    # Check notes for language requirements
    note = entry.get("note", "").lower()
    for lang in EXCLUDED_LANGUAGES:
        if lang.lower() in note:
            return True
    
    return False

def is_excluded_by_location(location: str, remote: str) -> bool:
    """Check if the location matches target criteria."""
    loc = location.lower()
    rem = str(remote).lower()
    
    # Target areas
    targets = ["estonia", "tallinn", "tartu", "kuressaare", "united states", "usa"]
    
    # Global/Broad indicators that make a country-restricted-looking role allowed
    broad_indicators = ["eu", "europe", "eea", "worldwide", "global", "anywhere", "estonia", "united states", "usa"]
    
    # Non-target countries/cities that are restricted-remote when listed alone
    non_target_countries = [
        "romania", "germany", "poland", "lithuania", "latvia", "finland", "sweden", 
        "france", "spain", "italy", "ukraine", "united kingdom", "uk", "canada", 
        "india", "philippines", "thailand", "singapore", "netherlands", "belgium", 
        "austria", "switzerland", "ireland", "bulgaria", "hungary", "denmark", "norway",
        "dubai", "bangkok", "romanian", "german", "polish", "latvian", "lithuanian", "canadian"
    ]
    
    # Check if location contains any of the non-target countries
    # e.g., "Romania (Remote)" or "Spain (Remote)"
    has_non_target_country = False
    for country in non_target_countries:
        # Use word boundaries or simple substring check (careful with 'uk' in 'luke' or 'ukraine')
        if country == "uk":
            if re.search(r'\buk\b', loc):
                has_non_target_country = True
                break
        else:
            if country in loc:
                has_non_target_country = True
                break
                
    # If it has a non-target country, check if it ALSO has a broad/global indicator or is one of our targets
    if has_non_target_country:
        has_broad_indicator = False
        for indicator in broad_indicators:
            if indicator == "eu":
                if re.search(r'\beu\b', loc):
                    has_broad_indicator = True
                    break
            else:
                if indicator in loc:
                    has_broad_indicator = True
                    break
        
        # If it has a non-target country but no broad indicator/target, exclude it!
        if not has_broad_indicator:
            return True

    # If it's in a target area, it's fine
    if any(t in loc for t in targets):
        return False
    
    # If it's remote, it's generally fine (Europe/Worldwide remote)
    if rem == "remote" or "remote" in loc:
        return False
    
    # Otherwise, if it's explicitly in a non-target country (and not remote), exclude it
    if rem == "onsite" or rem == "no":
        return True
        
    # If location is unknown and remote is unknown, keep it for safety? 
    # Or exclude if it's definitely not Estonia/US?
    if rem == "unknown" and not any(t in loc for t in targets):
         # If loc is just "unknown" or "—", keep it.
         if loc in ["unknown", "—", ""]:
             return False
         return True

    return False

def filter_jobs(data: dict, prefs: dict):
    seen = data.get("seen", {})
    filtered_seen = {}
    removed_counts = {
        "title_keyword": 0,
        "company": 0,
        "board": 0,
        "feedback": 0,
        "language": 0,
        "location": 0
    }
    
    for key, entry in seen.items():
        title = entry.get("title", "").lower()
        company = entry.get("company", "").lower()
        location = entry.get("location", "")
        remote = entry.get("remote", "")
        url = entry.get("url", key)
        
        # 1. Feedback Log
        if any(f_url in url for f_url in prefs["feedback_urls"]):
            removed_counts["feedback"] += 1
            continue
            
        # 2. Excluded Companies
        if any(c in company for c in prefs["companies"]):
            removed_counts["company"] += 1
            continue
            
        # 3. Excluded Boards / Domains
        domain = urlparse(url).netloc.lower()
        if any(b in domain for b in prefs["boards"]):
            removed_counts["board"] += 1
            continue
            
        # 4. Title Keywords
        if any(tk in title for tk in prefs["titles"]):
            removed_counts["title_keyword"] += 1
            continue
            
        # 5. Language Filter
        if is_excluded_by_language(entry.get("title", ""), entry):
            removed_counts["language"] += 1
            continue
            
        # 6. Location Filter
        if is_excluded_by_location(location, remote):
            removed_counts["location"] += 1
            continue
            
        # If it passed all filters, keep it
        filtered_seen[key] = entry
        
    return filtered_seen, removed_counts

def main():
    print("Loading preferences configuration and search queries...")
    prefs = parse_preferences()
    data = load_json(JSON_PATH)
    total_before = len(data.get("seen", {}))
    
    print(f"Filtering {total_before} jobs...")
    filtered_seen, counts = filter_jobs(data, prefs)
    total_after = len(filtered_seen)
    
    print("\nRemoval Summary:")
    for reason, count in counts.items():
        if count > 0:
            print(f" - {reason}: {count}")
            
    print(f"\nTotal removed: {total_before - total_after}")
    print(f"Remaining jobs: {total_after}")
    
    # Save the cleaned data
    data["seen"] = filtered_seen
    save_json(JSON_PATH, data)
    print(f"\nSuccessfully updated {JSON_PATH}")

if __name__ == "__main__":
    main()
