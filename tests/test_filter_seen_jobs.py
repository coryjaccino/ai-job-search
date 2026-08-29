import json
import tempfile
import unittest
from pathlib import Path

from tools.filter_seen_jobs import filter_jobs, parse_preferences


def preferences_data(**overrides):
    data = {
        "schema_version": 1,
        "excluded_title_keywords": ["graduate", "company", "vehicle"],
        "excluded_regions_and_job_boards": ["example-board.test"],
        "excluded_companies": ["unwanted corp"],
        "job_feedback": [
            {
                "date": "2026-08-28",
                "company": "Example",
                "title": "Example role",
                "issue": "Not suitable",
                "url": "https://example.test/jobs/123",
            }
        ],
    }
    data.update(overrides)
    return data


class ParsePreferencesTests(unittest.TestCase):
    def write_preferences(self, data):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        path = Path(temporary_directory.name) / "preferences.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_normalizes_exclusion_lists_and_extracts_feedback_urls(self):
        path = self.write_preferences(preferences_data(excluded_title_keywords=[" Graduate "]))

        preferences = parse_preferences(path)

        self.assertEqual(preferences["titles"], ["graduate"])
        self.assertEqual(preferences["feedback_urls"], ["https://example.test/jobs/123"])

    def test_rejects_invalid_schema_version(self):
        path = self.write_preferences(preferences_data(schema_version=2))

        with self.assertRaisesRegex(ValueError, "schema_version"):
            parse_preferences(path)

    def test_rejects_invalid_keyword_lists(self):
        path = self.write_preferences(preferences_data(excluded_title_keywords=["valid", 2]))

        with self.assertRaisesRegex(ValueError, "excluded_title_keywords"):
            parse_preferences(path)

    def test_rejects_feedback_without_required_fields(self):
        path = self.write_preferences(preferences_data(job_feedback=[{"date": "2026-08-28"}]))

        with self.assertRaisesRegex(ValueError, "requires non-empty"):
            parse_preferences(path)


class FilterJobsTests(unittest.TestCase):
    def setUp(self):
        self.preferences = parse_preferences(self._write_preferences(preferences_data()))

    def _write_preferences(self, data):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        path = Path(temporary_directory.name) / "preferences.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_singular_substring_matches_regular_plural_but_not_y_to_ies_plural(self):
        data = {
            "seen": {
                "graduate": {"title": "Graduate Analyst", "url": "https://good.test/graduate"},
                "graduates": {"title": "Graduates Programme", "url": "https://good.test/graduates"},
                "vehicles": {"title": "Vehicles Marketing Manager", "url": "https://good.test/vehicles"},
                "companies": {"title": "Companies Marketing Manager", "url": "https://good.test/companies"},
            }
        }

        filtered, counts = filter_jobs(data, self.preferences)

        self.assertEqual(set(filtered), {"companies"})
        self.assertEqual(counts["title_keyword"], 3)

    def test_filters_company_board_and_feedback_url(self):
        data = {
            "seen": {
                "company": {"title": "Marketing Manager", "company": "Unwanted Corp Ltd", "url": "https://good.test/company"},
                "board": {"title": "Marketing Manager", "company": "Good", "url": "https://example-board.test/job/1"},
                "feedback": {"title": "Marketing Manager", "company": "Good", "url": "https://example.test/jobs/123"},
            }
        }

        filtered, counts = filter_jobs(data, self.preferences)

        self.assertEqual(filtered, {})
        self.assertEqual(counts["company"], 1)
        self.assertEqual(counts["board"], 1)
        self.assertEqual(counts["feedback"], 1)


if __name__ == "__main__":
    unittest.main()