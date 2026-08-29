---
name: himalayas-search
version: 1.0.0
description: >
  Search current remote jobs from Himalayas' documented public API with mandatory
  country eligibility filtering. Use for remote Google Cloud, AI, analytics,
  marketing, consulting, and technology roles that must be open to a specified
  country such as Estonia or the United States. Trigger phrases: Himalayas jobs,
  remote jobs in Estonia, global remote jobs, remote jobs eligible in Europe.
context: fork
enabled: true
allowed-tools: Bash(bun run .agents/skills/himalayas-search/cli/src/cli.ts *)
---

# Himalayas Search Skill

Search Himalayas' documented public Remote Jobs API. The CLI requires one or more
candidate-residency countries and sends each country to the API **before** results
are returned. Himalayas includes worldwide roles in a country search; it does not
return roles restricted to unrelated countries.

## Scope and limitations

- This is a remote-job aggregator, not a guarantee that every result is suitable.
  The CLI preserves the API's `locationRestrictions`, timezone restrictions, and
  full description so `/scrape` can perform final language and eligibility checks.
- Use `--country Estonia` and/or `--country "United States"`; do not run an
  unqualified global feed.
- The API refreshes daily. The CLI makes at most one request per country per search
  and does not crawl the site.
- Use this skill for personal job-search purposes only. Do not bulk collect or
  redistribute data; review Himalayas' current terms before broader use.

## Commands

```bash
bun run .agents/skills/himalayas-search/cli/src/cli.ts search --country Estonia [flags]
```

### Search flags

- `--country <name|ISO>` — required; repeat for an OR list. Supported values include
  `Estonia` / `EE` and `United States` / `US`.
- `--query`, `-q <text>` — server-side free-text search.
- `--jobage <days>` — client-side maximum age using the API publication date.
- `--page <n>` — API search page, 1-indexed.
- `--limit`, `-n <n>` — cap merged results emitted.
- `--format json|table|plain` — default `json`.

### Examples

```bash
# Estonia-eligible Google Analytics roles, posted within 14 days
bun run .agents/skills/himalayas-search/cli/src/cli.ts search \
  -q "google analytics" --country Estonia --jobage 14 --format table

# Roles eligible in either Estonia or the United States
bun run .agents/skills/himalayas-search/cli/src/cli.ts search \
  -q "google cloud" --country EE --country US --jobage 14 --format table

```

## Output

Search JSON is `{ "meta": { "count", "page", "total" }, "results": [...] }`.
Each result includes `id`, `title`, `company`, `location`, `date`, `url`, plus the
structured `locationRestrictions`, `timezoneRestrictions`, `expiryDate`, and full
description required for final verification. There is intentionally no `detail`
command: Himalayas returns the complete structured description in the filtered
search response, while direct posting-page requests currently return `403`.

Data source: [Himalayas Remote Jobs API](https://himalayas.app/docs/remote-jobs-api).