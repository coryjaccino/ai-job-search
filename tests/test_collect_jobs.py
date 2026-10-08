import unittest
from datetime import date
from unittest.mock import patch

from tools.collect_jobs import (canonical_url, collect_query, deduplicate, markdown,
                               normalize_greenhouse, normalize_himalayas, prepare,
                               screen, validate_plan, read_json, PLAN)

TODAY = date(2026, 10, 8)


def job(number=1, **changes):
    row = {'id': str(number), 'url': f'https://example.com/jobs/{number}',
           'title': 'Google Ads consultant', 'company': 'Example', 'date': '2026-10-08',
           'description': 'Manage Google Ads and GA4.', 'source': 'test', 'work_mode': 'remote'}
    return dict(row, **changes)


class CollectionTests(unittest.TestCase):
    def test_paginates_until_total_exhausted(self):
        responses = [([job(1)], {'total': 2}), ([job(2)], {'total': 2})]
        with patch('tools.collect_jobs.fetch_page', side_effect=responses) as fetch:
            rows, coverage = collect_query(None, {'id': 'x', 'adapter': 'freehire'}, today=TODAY)
        self.assertEqual(len(rows), 2)
        self.assertEqual(fetch.call_count, 2)
        self.assertTrue(coverage['complete'])

    def test_budget_is_not_complete(self):
        with patch('tools.collect_jobs.fetch_page', return_value=([job()], {'total': 100})):
            _, coverage = collect_query(None, {'id': 'x', 'adapter': 'freehire'}, max_pages=1, today=TODAY)
        self.assertEqual(coverage['stop_reason'], 'page_budget')
        self.assertFalse(coverage['complete'])

    def test_empty_page_before_reported_total_is_incomplete(self):
        with patch('tools.collect_jobs.fetch_page', side_effect=[([job()], {'total': 10}), ([], {'total': 10})]):
            _, coverage = collect_query(None, {'id': 'x', 'adapter': 'himalayas'}, today=TODAY)
        self.assertFalse(coverage['complete'])
        self.assertEqual(coverage['stop_reason'], 'empty_page_before_reported_total')

    def test_repeated_page_is_incomplete(self):
        with patch('tools.collect_jobs.fetch_page', return_value=([job()], {'total': 100})):
            _, coverage = collect_query(None, {'id': 'x', 'adapter': 'freehire'}, today=TODAY)
        self.assertEqual(coverage['pages'], 2)
        self.assertEqual(coverage['stop_reason'], 'repeated_page')

    def test_himalayas_raw_dates_stop_at_date_window(self):
        with patch('tools.collect_jobs.fetch_page', return_value=([job(date='2026-08-01')], {'total': 100})):
            rows, coverage = collect_query(None, {'id': 'x', 'adapter': 'himalayas'}, today=TODAY)
        self.assertEqual(len(rows), 1)
        self.assertEqual(coverage['stop_reason'], 'date_window_exhausted')

    def test_failure_retains_previous_page_and_is_not_closure(self):
        with patch('tools.collect_jobs.fetch_page', side_effect=[([job()], {'total': 100}), RuntimeError('429')]):
            rows, coverage = collect_query(None, {'id': 'x', 'adapter': 'freehire'}, today=TODAY)
        self.assertEqual(len(rows), 1)
        self.assertFalse(coverage['complete'])
        self.assertNotIn('availability', rows[0])

    def test_jobicy_passes_opaque_cursor(self):
        responses = [([job(1)], {'cursor_supported': True, 'next_cursor': 'opaque', 'has_more': True}),
                     ([job(2)], {'cursor_supported': True, 'next_cursor': None, 'has_more': False})]
        with patch('tools.collect_jobs.fetch_page', side_effect=responses) as fetch:
            _, coverage = collect_query(None, {'id': 'x', 'adapter': 'jobicy'}, today=TODAY)
        self.assertEqual(fetch.call_args_list[1].args[5], 'opaque')
        self.assertTrue(coverage['complete'])

    def test_feed_snapshot_does_not_claim_market_exhausted(self):
        with patch('tools.collect_jobs.fetch_page', return_value=([job()], {'feed_only': True})):
            _, coverage = collect_query(None, {'id': 'x', 'adapter': 'rss'}, today=TODAY)
        self.assertFalse(coverage['complete'])

    def test_url_identity_keeps_job_ids_but_removes_tracking(self):
        self.assertEqual(canonical_url('http://www.example.com/jobs/1/?utm_source=x&id=9#top'),
                         'https://example.com/jobs/1?id=9')

    def test_duplicates_keep_observations_and_employer_evidence(self):
        rows = deduplicate([job(source='a', description=''), job(source='b', employer_verified=True)])
        row = next(iter(rows.values()))
        self.assertEqual(len(row['observations']), 2)
        self.assertTrue(row['employer_verified'])

    def test_same_title_different_postings_flagged_not_merged(self):
        rows = deduplicate([job(1), job(2)])
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({r['possible_duplicate_group'] for r in rows.values()}), 1)

    def test_unknown_business_terms_keep_review_without_score(self):
        result = screen(job(), {}, 14, TODAY)
        self.assertEqual(result['queue'], 'review')
        self.assertIsNone(result['fit_score'])

    def test_excluded_retained_and_pipeline_separate(self):
        self.assertEqual(screen(job(), {'excluded_title_keywords': ['consultant']}, 14, TODAY)['queue'], 'excluded')
        self.assertEqual(screen(job(description='Google Ads talent collective'), {}, 14, TODAY)['queue'], 'pipeline')

    def test_time_tracking_context_flagged_not_blindly_accepted(self):
        result = screen(job(description='GA4; we use Teamwork for time tracking'), {}, 14, TODAY)
        self.assertTrue(any('Time-tracking' in flag for flag in result['flags']))

    def test_publication_and_discovery_distinct_and_rerun_idempotent(self):
        baseline = {'seen': {job()['url']: job()}}
        records = prepare([job()], {'seen': {}}, baseline, {}, 14, TODAY)
        self.assertFalse(next(iter(records.values()))['new_to_collection'])
        records = prepare([job(date='2026-10-01')], {'seen': {}}, {'seen': {}}, {}, 14, TODAY)
        row = next(iter(records.values()))
        self.assertTrue(row['new_to_collection'])
        self.assertFalse(row['newly_published_today'])
        again = prepare([job()], {'seen': {job()['url']: {'first_collected': '2026-10-01'}}}, {'seen': {}}, {}, 14, TODAY)
        self.assertFalse(next(iter(again.values()))['new_to_collection'])

    def test_greenhouse_updated_date_not_publication(self):
        row = normalize_greenhouse({'id': 1, 'title': 'GA4', 'absolute_url': job()['url'],
                                    'updated_at': '2026-10-08'}, {'company': 'Example'})
        self.assertIsNone(row['date'])

    def test_report_shows_all_review_rows(self):
        records = prepare([job(n, company=f'Company {n}') for n in range(35)],
                          {'seen': {}}, {'seen': {}}, {}, 14, TODAY)
        report = {'date': TODAY.isoformat(), 'records': records, 'coverage': [],
                  'counts': {}, 'manual_sources': []}
        text = markdown(report)
        self.assertIn('(35)', text)
        self.assertIn('Company 34', text)

    def test_real_plan_valid(self):
        validate_plan(read_json(PLAN, {}))


if __name__ == '__main__':
    unittest.main()