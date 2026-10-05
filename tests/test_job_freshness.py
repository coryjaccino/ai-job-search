import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from tools.job_freshness import freshness, rank_candidates, sort_key
from tools import generate_seen_jobs_md as summary


TODAY = date(2026, 10, 4)


def job(age=None, **overrides):
    entry = {'status': 'new', 'fit': 'high', 'title': 'Google Ads specialist', 'company': 'Example', 'first_seen': TODAY.isoformat()}
    if age is not None:
        entry['posted'] = (TODAY - timedelta(days=age)).isoformat()
    entry.update(overrides)
    return entry


class FreshnessTests(unittest.TestCase):
    def test_boundaries(self):
        for age, band in [(0, 'Fresh'), (7, 'Fresh'), (8, 'Current'), (14, 'Current'), (15, 'Aging'), (30, 'Aging'), (31, 'Older'), (60, 'Older'), (61, 'Archive candidate')]:
            with self.subTest(age=age):
                self.assertEqual(freshness(job(age), TODAY)['band'], band)

    def test_unknown_invalid_and_future_dates(self):
        for value in [None, '', 'bad', '2026-02-30', '2026-10-05', 42]:
            with self.subTest(value=value):
                info = freshness(job(posted=value), TODAY)
                self.assertEqual(info['band'], 'Undated')
                self.assertIsNone(info['age_days'])

    def test_collection_and_verification_never_reset_age(self):
        self.assertEqual(freshness(job(80, last_verified_open=TODAY.isoformat()), TODAY)['age_days'], 80)
        self.assertEqual(freshness(job(last_checked=TODAY.isoformat()), TODAY)['band'], 'Undated')

    def test_original_date_precedence_and_confidence(self):
        info = freshness(job(1, published_date='2026-08-01', publication_confidence='verified'), TODAY)
        self.assertEqual(info['age_days'], 64)
        self.assertEqual(info['confidence'], 'verified')
        self.assertEqual(freshness(job(posted='2026-10-01T12:30:00Z'), TODAY)['age_days'], 3)
        self.assertEqual(freshness(job(1), TODAY)['confidence'], 'source-reported')

    def test_selection_defaults_and_explicit_options(self):
        seen = {'fresh': job(7), 'current': job(14), 'aging': job(15), 'old': job(80), 'unknown': job(), 'ranked': job(1, status='ranked'), 'closed': job(1, availability='closed'), 'skipped': job(1, status='skipped')}
        before = json.dumps(seen, sort_keys=True)
        self.assertEqual(set(rank_candidates(seen, today=TODAY)), {'fresh', 'current'})
        self.assertEqual(set(rank_candidates(seen, days=30, today=TODAY)), {'fresh', 'current', 'aging'})
        self.assertIn('unknown', rank_candidates(seen, include_undated=True, today=TODAY))
        self.assertIn('old', rank_candidates(seen, days=None, today=TODAY))
        self.assertNotIn('unknown', rank_candidates(seen, days=None, today=TODAY))
        self.assertIn('ranked', rank_candidates(seen, all_statuses=True, today=TODAY))
        self.assertNotIn('old', rank_candidates(seen, all_statuses=True, today=TODAY))
        self.assertEqual(before, json.dumps(seen, sort_keys=True))

    def test_sort_fit_then_deadline_then_age(self):
        rows = [('a', job(1, rank_score=80)), ('b', job(10, rank_score=90)), ('c', job(5, rank_score=80, deadline='2026-10-06')), ('d', job(2, rank_score=80))]
        self.assertEqual([k for k, _ in sorted(rows, key=lambda item: sort_key(item, TODAY))], ['b', 'c', 'a', 'd'])
        self.assertLess(sort_key(('e', job(4, evaluation_score=91, rank_score=70)), TODAY), sort_key(rows[1], TODAY))


class SummaryTests(unittest.TestCase):
    def test_sections_archive_visibility_and_no_database_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'seen.json'
            data = {'seen': {'fresh': job(1, title='Fresh | role'), 'old': job(40, title='Older role'), 'archive': job(80, title='Archive role'), 'unknown': job(title='Undated role'), 'closed': job(1, title='Closed role', availability='closed')}}
            path.write_text(json.dumps(data))
            before = path.read_bytes()
            with patch.object(summary, 'JSON_PATH', path), patch.object(summary, 'load_company_links', return_value={}):
                text = summary.generate(today=TODAY)
                self.assertIn('## Fresh (1)', text)
                self.assertIn('## Older (1)', text)
                self.assertIn('## Undated (1)', text)
                self.assertNotIn('Archive role', text)
                self.assertNotIn('Closed role', text)
                self.assertIn('Archive role', summary.generate(include_archive=True, today=TODAY))
                self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()