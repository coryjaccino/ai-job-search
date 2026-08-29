# Himalayas Remote Jobs API reference

Verified 2026-08-28 against Himalayas' documented public API.

## Access

- Documentation: `https://himalayas.app/docs/remote-jobs-api`
- Search endpoint: `GET https://himalayas.app/jobs/api/search`
- No API key or authentication is required.
- The API refreshes daily; respect HTTP 429 and avoid polling more often than needed.
- Search API parameters used by this CLI are server-side: `q`, `country`, `sort`,
  and `page`. A country search includes worldwide roles by default.

## Parameters

| API parameter | CLI flag | Notes |
|---|---|---|
| `q` | `--query` | Free-text server-side search. |
| `country` | `--country` | ISO-3166 alpha-2 uppercase country code. One API request is made per CLI country. |
| `sort=recent` | fixed | Freshest API ordering. |
| `page` | `--page` | 1-indexed search-results page. |

The API also documents `worldwide`, `exclude_worldwide`, `seniority`,
`employment_type`, `company`, and `timezone`; this focused initial CLI does not
expose them until a real search need justifies more flags.

## Response fields used

`jobs[]` contains `guid`, `title`, `companyName`, `employmentType`, `seniority`,
`locationRestrictions`, `timezoneRestrictions`, `description`, `pubDate`,
`expiryDate`, `applicationLink`, and `categories`.

`locationRestrictions: []` represents worldwide availability. The current response
uses country-name strings; the CLI also accepts future object-shaped restrictions
with `alpha2`, `name`, or `slug` fields.

## Detail requests

The filtered search response is the detail record for this skill: it includes the
full description, restrictions, publication date, expiry date, and application URL.
Direct HTML requests to public posting pages returned HTTP 403 during the 2026-08-28
verification, so this CLI deliberately does not expose a broken `detail` command.