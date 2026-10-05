"""Shared, non-mutating posting freshness and shortlist rules.

Publication dates never fall back to collection or verification dates.
Legacy `posted` dates are source-reported, not independently verified.
"""

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path


def parse_date(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.strip().replace('Z', '+00:00')).date()
    except ValueError:
        return None


def freshness(entry, today=None):
    today = today or datetime.now(timezone.utc).date()
    # An explicitly supplied original date takes precedence, even if invalid.
    value = entry.get('published_date') or entry.get('posted')
    published = parse_date(value)
    confidence = entry.get('publication_confidence', 'source-reported' if published else 'unknown')
    if confidence not in ('verified', 'source-reported', 'uncertain', 'unknown'):
        confidence = 'uncertain'
    age = (today - published).days if published else None
    if age is not None and age < 0:
        age = None
        confidence = 'uncertain'
    band = 'Undated'
    if age is not None:
        band = next(label for limit, label in ((7, 'Fresh'), (14, 'Current'), (30, 'Aging'), (60, 'Older'), (float('inf'), 'Archive candidate')) if age <= limit)
    return {'age_days': age, 'band': band, 'published_date': published.isoformat() if published else None, 'confidence': confidence}


def rank_candidates(seen, days=14, include_undated=False, all_statuses=False, today=None):
    """Apply freshness/workflow selection; tracker and eligibility gates are separate."""
    selected = {}
    for key, entry in seen.items():
        if entry.get('status') in ('applied', 'expired', 'skipped') or entry.get('availability') == 'closed':
            continue
        if not all_statuses and entry.get('status') != 'new':
            continue
        age = freshness(entry, today)['age_days']
        if (age is None and include_undated) or (age is not None and (days is None or age <= days)):
            selected[key] = entry
    return selected


def sort_key(item, today=None):
    _, entry = item
    score = entry.get('evaluation_score', entry.get('rank_score'))
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        score = {'high': 75, 'medium': 50, 'low': 25}.get(entry.get('fit'), 0)
    today = today or datetime.now(timezone.utc).date()
    deadline = parse_date(entry.get('deadline'))
    remaining = (deadline - today).days if deadline else None
    urgent = remaining is not None and 0 <= remaining <= 7
    age = freshness(entry, today)['age_days']
    return (-score, not urgent, remaining if urgent else float('inf'), age if age is not None else float('inf'), str(entry.get('title', '')), str(item[0]))


def main():
    parser = argparse.ArgumentParser(description='Read-only rank candidate selection by posting age.')
    parser.add_argument('--input', type=Path, default=Path(__file__).resolve().parent.parent / 'job_scraper/seen_jobs.json')
    window = parser.add_mutually_exclusive_group()
    window.add_argument('--days', type=int, default=14)
    window.add_argument('--all-ages', action='store_true')
    parser.add_argument('--include-undated', action='store_true')
    parser.add_argument('--all', action='store_true', help='Include previously ranked/evaluated records; does not widen age window.')
    args = parser.parse_args()
    if args.days < 0:
        parser.error('--days must be non-negative')
    seen = json.loads(args.input.read_text(encoding='utf-8')).get('seen', {})
    selected = rank_candidates(seen, None if args.all_ages else args.days, args.include_undated, args.all)
    print(json.dumps({'count': len(selected), 'seen': selected}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()