# Auditable daily collection

From the repository root, run `python3 tools/collect_jobs.py`.
Configuration: `/Users/coryjaccino/Development/ai-job-search/.claude/skills/job-scraper/collection-plan.json`.
Runner: `/Users/coryjaccino/Development/ai-job-search/tools/collect_jobs.py`.

The runner uses Python's standard library and the existing Bun FreeHire CLI.
No paid service or new dependency is required. TLS verification stays enabled.

## Sources and limits

- Himalayas: country-filtered keyword search, raw-page date-window stopping.
- FreeHire: existing remote keyword CLI, 50 results/page; no invented geography facets.
- Jobicy: opaque cursor pagination of its public seven-day feed.
- We Work Remotely: marketing and other RSS snapshots; never described as exhaustive.
- Greenhouse and Lever: configured employer boards, full descriptions where provided.
- LinkedIn is intentionally not bulk/schedule automated. Gated and unconnected sources
  are listed as not automated; configuration is not a claim of actual coverage.

Each query has a six-page default budget. A budget stop is incomplete, not an empty
market. Source errors stop further queries against that source. Requests are paced;
there is no bypass of rate limits or access controls. For diagnostics:

```sh
python3 tools/collect_jobs.py --sources himalayas --query-limit 1 --max-pages 2 --no-state-update
```

## Output and state

`reports/search-<UTC timestamp>/run.json` contains every collected record,
source observation, coverage count, exclusion and keyword signal. `review.md`
shows every new keyword-relevant posting, pipeline and excluded record without
a five-result cap. `progress.json` checkpoints coverage during collection.
All these personal outputs are gitignored.

`job_scraper/collection_state.json` retains collection history for next-run deduplication.
Writes are atomic. The runner does not mutate `seen_jobs.json`, submit anything,
or create application-tracker rows. Run only one collector at a time: atomic writes
protect file integrity, but concurrent history merges are not supported.

Exact canonical URLs are deduplicated. Same-company/title postings at different
URLs are flagged as possible duplicates, not silently merged. Original dates,
source-reported publication dates and first discovery remain separate. Greenhouse
`updated_at` and collection dates are never used as original publication dates.

## Full fit review is a separate mandatory step

Keyword relevance is **not** a high-fit score. The review queue may contain jobs
that merely mention GA4 or Google Ads in passing. Read full descriptions, verify
employer availability, apply the canonical profile/preferences and score all
dimensions before presenting verified strong matches. Time-tracking mentions,
work arrangements, language requirements and business invoicing need contextual
review. Unknown business terms do not automatically exclude a promising posting.

Use **Data Studio** in user-facing reports. Historical product names remain search
aliases. Never count talent pipelines, reposts, or older discoveries as newly
published assignments. Source dates may be aggregator refreshes.

## Scheduling and coverage expansion

No scheduler is installed automatically. Once a complete run and full fit review
are satisfactory, configure a local daily scheduler for this command and review
14 days of source yield. The scheduler performs collection, not unattended AI scoring.

The initial employer set comes from existing verified search records and is small.
Expand it by researching Google Ads/Marketing Platform partners and checking each
career page for a real board token. Never invent 100–200 employer connectors to
meet a numerical target. A useful company directory entry is not an open posting.