#!/usr/bin/env python3
"""Validate the canonical remote-job-source registry."""

import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / ".claude" / "skills" / "job-scraper" / "remote-sources.json"
VALID_CLASSES = {"job_board", "aggregator", "startup_marketplace", "startup_job_board", "talent_marketplace", "freelance_marketplace", "staffing", "editorial_lead_source", "meta_directory", "inactive"}
VALID_POLICIES = {"remote_only", "remote_friendly", "mixed", "unknown"}
VALID_METHODS = {"api_or_websearch", "api_rss_or_websearch", "api_rss_or_manual", "websearch", "manual", "none"}
VALID_TIERS = {"core", "secondary", "manual", "staffing", "discovery", "inactive"}


def is_url(value: object) -> bool:
    return isinstance(value, str) and urlparse(value).scheme == "https" and bool(urlparse(value).netloc)


def validate(data: object) -> list[str]:
    errors = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return ["registry must be an object with schema_version: 1"]
    try:
        date.fromisoformat(data["last_audit_date"])
    except (KeyError, TypeError, ValueError):
        errors.append("last_audit_date must be an ISO-8601 date")

    profiles = data.get("query_profiles")
    if not isinstance(profiles, dict) or not profiles:
        errors.append("query_profiles must be a non-empty object")
        profiles = {}
    else:
        for name, terms in profiles.items():
            if not isinstance(name, str) or not isinstance(terms, list) or not terms or not all(isinstance(term, str) and term.strip() for term in terms):
                errors.append(f"query profile {name!r} must be a non-empty list of non-empty strings")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        return errors + ["sources must be a non-empty list"]
    ids = set()
    required = ("id", "name", "class", "remote_policy", "coverage", "focus", "browse_url", "websearch_scope", "posting_pattern", "search_method", "tier", "access", "last_verified", "notes")
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = [key for key in required if key not in source]
        if missing:
            errors.append(f"{label} missing keys: {', '.join(missing)}")
            continue
        source_id = source["id"]
        if not isinstance(source_id, str) or not source_id or source_id in ids:
            errors.append(f"{label}.id must be a unique non-empty string")
        ids.add(source_id)
        if source["class"] not in VALID_CLASSES:
            errors.append(f"{source_id}: invalid class")
        if source["remote_policy"] not in VALID_POLICIES:
            errors.append(f"{source_id}: invalid remote_policy")
        if source["search_method"] not in VALID_METHODS:
            errors.append(f"{source_id}: invalid search_method")
        if source["tier"] not in VALID_TIERS:
            errors.append(f"{source_id}: invalid tier")
        if not is_url(source["browse_url"]):
            errors.append(f"{source_id}: browse_url must be an https URL")
        if not isinstance(source["focus"], list) or any(profile not in profiles for profile in source["focus"]):
            errors.append(f"{source_id}: focus must contain only defined query profiles")
        try:
            date.fromisoformat(source["last_verified"])
        except (TypeError, ValueError):
            errors.append(f"{source_id}: last_verified must be an ISO-8601 date")
        automated = source["tier"] in {"core", "secondary", "staffing"}
        if automated and source["search_method"] not in {"api_or_websearch", "api_rss_or_websearch", "websearch"}:
            errors.append(f"{source_id}: automated tiers require an API/WebSearch method")
        if automated and not source["websearch_scope"].startswith("site:"):
            errors.append(f"{source_id}: automated tiers require a site: websearch_scope")
        if source["tier"] == "inactive" and source["search_method"] != "none":
            errors.append(f"{source_id}: inactive sources must use search_method none")
        if source["tier"] == "inactive" and source["websearch_scope"]:
            errors.append(f"{source_id}: inactive sources must have an empty websearch_scope")
    return errors


def main() -> int:
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"remote-sources: unable to read {REGISTRY_PATH}: {exc}")
        return 1
    errors = validate(data)
    if errors:
        print(f"remote-sources: {len(errors)} validation failure(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"remote-sources: OK ({len(data['sources'])} sources, {len(data['query_profiles'])} query profiles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())