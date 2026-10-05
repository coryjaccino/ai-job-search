# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

## Installed portal CLIs (primary for `/scrape`)

By default, `/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first; a source preset restricts discovery to its registry allowlist. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

## How to Write a `/scrape` Prompt

Use this pattern:

```text
/scrape <where> <what> [filters]
```

- `<where>` is an optional source group such as `estonia-local`, `cloud-partners`, or `remote-first`. It controls **where listings are found**. Omit it to search the normal enabled sources.
- `<what>` is an ordinary job title, description, skill, or keywords, such as `cloud architect`, `google ads`, or `data engineer`.
- `[filters]` constrain the job location or remote-work eligibility, work arrangement, or posting age.

```text
/scrape estonia-local data engineer
/scrape remote-first cloud architect --country Estonia --remote
/scrape general-portals google ads --country "United States" --remote
/scrape cloud-partners ai engineer --city Tallinn --hybrid
/scrape technical consultant --region Europe --remote --days 7
```

### Prompt Filters

| Filter | Purpose | Example |
|---|---|---|
| `--country <name>` | Job location or remote-candidate eligibility country | `--country Estonia` |
| `--city <name>` | Specific job city | `--city Tallinn` |
| `--region <name>` | Broader job or remote-eligibility region | `--region Europe` |
| `--remote` / `--hybrid` / `--onsite` | Required work arrangement; use only one | `--remote` |
| `--days <1-30>` | Maximum posting age; overrides the 14-day default | `--days 7` |

Quote filter values containing spaces, such as `--country "United States"`. Repeat `--country` for an OR list, for example `--country Estonia --country "United States"`.

## Search Sites & Target Companies

### 1. General & Tech Job Portals (Primary)
- **linkedin.com/jobs** — LinkedIn job listings (filter: Estonia / United States / Remote); also covered by `linkedin-search` CLI
- **Indeed.com** — International job board (filter: remote, US, Estonia)
- **freehire.me** — Tech-focused aggregator, covered by `freehire-search` CLI

**Shortcut:** `/scrape general-portals` searches only these three general portals using Priority G.

### 2. Estonian Local Job Portals & Recruiters
- **workinestonia.com/job/** — English-language jobs in Estonia (highly relevant for English-speaking tech roles)
- **cv.ee** (CV-Online) — One of Estonia's largest and most established job portals, frequently featuring English-language roles in tech, marketing, and administration.
- **cvkeskus.ee** (CV Keskus) — A leading Estonian job board with a massive selection of local vacancies, including tech and multinational listings.
- **ittalent.ee** (IT Talent) - High-end tech recruitment (unicorns).
- **humanlab.ee** (Human Lab) - Startup-focused technical hiring.
- **tripod.ee** (Tripod) - Executive & senior cloud search.
- **meetfrank.com** (MeetFrank) — A highly popular app-based recruitment platform and web job market in Estonia and the Baltics, specifically geared toward startup, technology, and digital marketing roles in English.

**Shortcut:** `/scrape estonia-local` searches only these seven portals using the Priority E queries below.

### 3. Google Cloud Partners (Target Companies)
These are primary target employers based in Estonia matching your deep GCP, AI/ML, and Cloud Architecture expertise. Partner directory pages are linked to reference their specialization and tailor direct outreach.

* **Estonia-Based Partners / Premier Partners:**
  - **Mooncascade** — [Website](https://www.mooncascade.com) | [Google Partner Directory](https://cloud.google.com/find-a-partner/partner/mooncascade) — Highly respected product development and cloud/AI consultancy.
  - **KK Veebiguru OÜ** — [Website](https://www.veebiguru.ee) | [Google Partner Directory](https://partnersdirectory.withgoogle.com/partners/6791900180) — Web development and localized cloud solutions provider.
- **Nortal** — [Website](https://nortal.com) — Multinational strategic change and technology company.
- **Helmes** — [Website](https://helmes.com) — Digital services and consulting company.
- **MindTitan** — [Website](https://mindtitan.com) — AI & Machine Learning solutions.
- **Pactum** — [Website](https://pactum.com) — AI-driven contract negotiation.

**Shortcut:** `/scrape cloud-partners` searches only these six Google Cloud partners using Priority 5a.

### 4. Google Ads Partners & Performance Marketing (Target Companies)
These are key target companies matching your elite Google Ads, PPC, SEM, and growth marketing expertise.
* **Estonia-Based Premier Partners:**
  - **Holini** — [Website](https://holini.com) | [Google Partner Directory](https://partnersdirectory.withgoogle.com/partners/7528825949) — Core focus on digital analytics, marketing automation, and cloud tracking infrastructure. Specialized agency in analytics and advanced search marketing.
  - **ePPC** — [Website](https://eppcdigital.com) | [Google Partner Directory](https://partnersdirectory.withgoogle.com/partners/1051623899) — Joint Google Ads & GCP Premier Partner specializing in data-driven digital marketing and analytics. Premier Partner in Search, Mobile, and Display Ads.
  - **7p.marketing OÜ** — [Website](https://7p.marketing) | [Google Partner Directory](https://partnersdirectory.withgoogle.com/partners/4019096845) — Performance marketing and analytics consultancy. Specialized Performance Agency.
  - **Mediabrands Digital** — [Website](https://mbd.ee) | [Google Partner Directory](https://partnersdirectory.withgoogle.com/partners/5230817227) — Major digital agency with extensive capabilities in cloud-based marketing. Leading digital media agency.

**Shortcut:** `/scrape ads-partners` searches only these four Google Ads partners using Priority 5b.

### 5. Remote-First & Niche Job Portals

The canonical, audited source registry is [`remote-sources.json`](remote-sources.json). It records a source's public browse URL, verified `site:` scope, posting-path observations, source type, access limitations, geographic coverage, tier, and audit date. Do not add a domain to a query block merely because it ends in `.com`: a job board's root, browse page, individual posting path, and its own corporate careers page can be different surfaces.

| Tier | `/scrape` behavior | Sources |
|---|---|---|
| **Core** | Search on every `/scrape remote-first` run. | Remote OK, Himalayas (installed `himalayas-search` CLI first), Jobicy, Remote.com Jobs, Remote.io, Working Nomads, NoDesk, Dynamite Jobs, Remote100K, We Work Remotely |
| **Secondary** | Search with `/scrape remote-first all`, or rotate after core sources. | Remote.co, EU Remote Jobs, Remote Rocketship, Jobspresso, DailyRemote, JustRemote, Wellfound, YC Startup Jobs, Built In Remote, Jobgether, SkipTheDrive, Rat Race Rebellion |
| **Manual / gated** | Report when relevant; do not claim complete automated coverage. | Remotive, FlexJobs, Virtual Vocations, Arc, Contra, Toptal, Upwork, Outsourcely, TryRemotely |
| **Staffing** | Search only through `/scrape us-staffing`. | Robert Half, Creative Circle, Onward Search |
| **Discovery / inactive** | Do not search for postings. | Job Board Search (meta-directory); Pangian and Hubstaff Talent (currently inactive/unverified) |

**Shortcut:** `/scrape remote-first` runs the registry's **core** sources. `/scrape remote-first all` adds **secondary** sources. `cloud`, `marketing`, `ai`, and `general` select the corresponding query profile in the registry; user-supplied focus terms further narrow it. The marketplace/freelance sources are better searched directly after signing in. Sources with official APIs or RSS feeds should be considered for a dedicated CLI via `/add-portal` before relying on WebSearch.

**Staffing shortcut:** `/scrape us-staffing` searches only Robert Half, Creative Circle, and Onward Search.

### 6. Estonian Tech Companies & Recruiters (Foreigner-Friendly)
These are Estonian companies known to be open to hiring international talent, plus tech recruiters/agencies that place foreign candidates. Strategic angles are documented in `target_companies.md`.

* **Product Companies:**
  - **Bolt** — [Website](https://bolt.eu) | [Careers](https://bolt.eu/careers/) — Mobility & logistics; AI/Vertex AI angle.
  - **Wise** — [Website](https://wise.com) | [Careers](https://wise.com/careers/) — FinTech; Cloud Security & Compliance angle.
  - **Pipedrive** — [Website](https://pipedrive.com) | [Careers](https://www.pipedrive.com/en/jobs) — CRM; Google Analytics/Ads integration angle.
  - **Glia** — [Website](https://glia.com) | [Careers](https://glia.com/company/careers) — AI-powered customer service; Agentic AI angle.
  - **Starship Technologies** — [Website](https://starship.xyz) | [Careers](https://starship.xyz/careers/) — Autonomous delivery; Data Engineering & AI angle.
  - **Salv** — [Website](https://salv.com) | [Careers](https://salv.com/careers) — Security & AI angle.
  - **Scoro** — [Website](https://scoro.com) | [Careers](https://scoro.com/careers) — Project Management & Cloud Architecture angle.
  - **DataArt** — [Website](https://dataart.com) | [Careers](https://dataart.com/careers/) — Cloud consulting; GCP Specializations angle.
  - **Veriff** — [Website](https://veriff.com) — Identity verification and fraud prevention platform.

* **Recruiters / Agencies:**
  - **Moving2Europe** — [Website](https://moving2europe.eu) — Relocation & placement assistance; knows which GCP firms hire US citizens.
  - **Relocate.me** — [Website](https://relocate.me) — Job search with relocation filter; use "Estonia" filter for sponsorship-offering firms.
  - **IT Talent** — [Website](https://ittalent.ee) — Startup-focused technical hiring.
  - **Human Lab** — [Website](https://humanlab.ee) — Executive & Senior Cloud Search.
  - **Tripod** — [Website](https://tripod.ee) — Nordic/Baltic job marketplace app.

**Shortcut:** `/scrape estonia-targets` searches only these product companies and recruiters using Priority 5c.

## Language Filter (Default — Always Apply)

**Exclude all postings requiring any language other than English or Spanish. This applies to both the job title and description body:**

1. **Skip any posting whose title contains characters indicating a local-language audience** other than English or Spanish (e.g. non-ASCII Cyrillic or localized accents not relevant to English/Spanish titles).
2. **Skip any posting where the description is predominantly in a language other than English or Spanish**.
3. **Skip any posting that explicitly requires fluency in any language other than English or Spanish**.

**Excluded languages (automatically skip):** Arabic, Bulgarian, Dutch, Finnish, French, German, Greek, Hungarian, Polish, Romanian, Russian.

## Location Focus

Focus on **United States** and **Estonia** primarily:

- **United States** — remote roles only (no relocation)
- **Estonia** — Tallinn, Tartu, Kuressaare, or anywhere in Estonia: include good-fit remote, hybrid, and on-site roles with Estonian employers, preferring remote then hybrid. Verify employer and work location before treating an on-site role as eligible.
- **Europe (remote)** — fully remote roles across the EU/EEA
- **Worldwide (remote)** — fully remote roles open globally

Current role priority (clarified October 4, 2026): Google Ads/PPC, Google Analytics/GA4, Google Cloud, Looker Studio (formerly Data Studio), and relevant BigQuery work. Email marketing/tracking is a supporting capability, not a search focus or résumé claim. Do not apply a remote-only filter to all Estonian-employer searches.

### Location Filters in Prompts

A source group controls **where listings are found**; a location filter controls **where the job can be performed or where the candidate may reside**. For example:

```text
/scrape remote-first data engineer --country Estonia --remote
```

This searches remote-first portals but keeps roles located in Estonia or explicitly open to candidates based in Estonia. Europe-wide, EU/EEA-wide, worldwide, and global remote roles are compatible when their posting does not exclude Estonia.

Use `--country <name>`, `--city <name>`, or `--region <name>` for location or eligibility, and one of `--remote`, `--hybrid`, or `--onsite` for work arrangement. A source group and a country filter can be combined even when unusual: the group limits listing sources; the filter limits eligible jobs.

## Query Categories

Queries are grouped by priority. Each query targets US remote and Estonia specifically.

### Source Preset Registry

This table is the canonical mapping for source-scoped `/scrape` commands. A preset limits the run to its mapped query groups and source domains; trailing words narrow the role focus without expanding that allowlist.

| Preset | Query group(s) | Source scope |
|---|---|---|
| `general-portals` | Priority G | LinkedIn, Indeed, and FreeHire |
| `estonia-local` | Priority E | Seven local Estonian portals and recruiters from Section 2 |
| `cloud-partners` | Priority 5a | Six Google Cloud partners from Section 3 |
| `ads-partners` | Priority 5b | Four Google Ads partners from Section 4 |
| `remote-first` | Priority 6 | Core remote sources; add `all` for secondary sources as defined in `remote-sources.json` |
| `estonia-targets` | Priority 5c | Estonian product companies and recruiters from Section 6 |
| `us-staffing` | Priority 7 | Robert Half, Creative Circle, and Onward Search |

`remote-first` supports the documented modifiers `cloud`, `marketing`, and `all`. Any other trailing text on any preset is treated as a role-focus filter.

**Prompt pattern:** `/scrape <source preset> <job focus> [filters]`. The preset limits where the scraper searches; focus terms and filters narrow results without adding sources.

```text
/scrape estonia-targets cloud architect --country Estonia
```

### Query Category Index

Every executable query group in this document is listed here. Parent groups organize their labeled subgroups; a preset runs only the group(s) shown for it in the Source Preset Registry.

| Query group | Purpose | Invocation, when applicable |
|---|---|---|
| Priority G | General job portals | `/scrape general-portals` |
| Priority E | Estonian local portals and recruiters | `/scrape estonia-local` |
| Priority 1 | Google Ads, Google Cloud, marketing, PPC, SEO, and AI search roles | `/scrape <role focus>` |
| Priority 2 | AI/ML engineering and cloud roles | `/scrape <role focus>` |
| Priority 3 | Technical consulting and solutions roles | `/scrape <role focus>` |
| Priority 4 | Broader technical roles | `/scrape <role focus>` |
| Priority 5 | Target-company direct web searches (parent group) | `/scrape broad` includes 5a–5c |
| Priority 5a | Google Cloud partners | `/scrape cloud-partners` |
| Priority 5b | Google Ads partners | `/scrape ads-partners` |
| Priority 5c | Estonian target companies and recruiters | `/scrape estonia-targets` |
| Priority 6 | Remote-first job portals (parent group) | `/scrape remote-first` |
| Priority 6 | Registry-driven remote sources and focus profiles | `/scrape remote-first [cloud\|marketing\|ai\|general\|all]` |
| Priority 7 | US staffing portals | `/scrape us-staffing` |

### Priority G: General Portals (`/scrape general-portals`)

Use the installed `linkedin-search` and `freehire-search` CLIs plus the Indeed WebSearch fallback. Do not run other installed portal CLIs for this preset.

```
site:linkedin.com/jobs USA OR Estonia OR remote
site:indeed.com/viewjob USA OR Estonia OR remote
site:freehire.me USA OR Estonia OR remote
```

### Priority E: Estonian Local Portals (`/scrape estonia-local`)

Run these seven WebSearch fallback queries only when the `estonia-local` preset is requested. If one of these domains has a dedicated installed CLI skill, use that CLI for the domain instead. Keep the configured profile keywords, English/Spanish language filter, and 14-day date filter when evaluating results.

```
site:workinestonia.com/job/ "google" OR "cloud" OR "ai" OR "marketing" OR "analytics" OR "technical"
site:cv.ee "google" OR "cloud" OR "ai" OR "marketing" OR "analytics" OR "technical"
site:cvkeskus.ee "google" OR "cloud" OR "ai" OR "marketing" OR "analytics" OR "technical"
site:ittalent.ee "google" OR "cloud" OR "ai" OR "engineer" OR "technical"
site:humanlab.ee "google" OR "cloud" OR "ai" OR "marketing" OR "technical"
site:tripod.ee "google" OR "cloud" OR "ai" OR "marketing" OR "technical"
site:meetfrank.com "google" OR "cloud" OR "ai" OR "marketing" OR "analytics" OR "technical"
```

### Priority 1: Google Ads / Google Cloud / Digital Marketing / PPC / SEO & AI Search

These match your strongest and most desired career direction.

**Focus shortcut:** Use `/scrape marketing`, `/scrape google ads`, `/scrape google cloud`, or another role keyword to prioritize this category and generate focus-specific queries. Add a source preset first to constrain where to search, e.g. `/scrape ads-partners google ads`.

```
site:linkedin.com/jobs "ai search" USA OR Estonia OR remote
site:linkedin.com/jobs "analyst" USA OR Estonia OR remote
site:linkedin.com/jobs "data studio" USA OR Estonia OR remote
site:linkedin.com/jobs "digital marketing" "google ads" remote
site:linkedin.com/jobs "google ads" USA OR Estonia OR remote
site:linkedin.com/jobs "google analytics" USA OR Estonia OR remote
site:linkedin.com/jobs "google cloud" USA OR Estonia OR remote
site:linkedin.com/jobs "google tag manager" USA OR Estonia OR remote
site:linkedin.com/jobs "looker studio" USA OR Estonia OR remote
site:linkedin.com/jobs "organic search" USA OR Estonia OR remote
site:linkedin.com/jobs "paid search" USA OR Estonia OR remote
site:linkedin.com/jobs "PPC specialist" USA OR Estonia OR remote
site:linkedin.com/jobs "reporting" USA OR Estonia OR remote
site:linkedin.com/jobs "search engine" USA OR Estonia OR remote
site:linkedin.com/jobs "sem" USA OR Estonia OR remote
site:linkedin.com/jobs "seo" USA OR Estonia OR remote
site:workinestonia.com/job/ "digital marketing" OR "ppc" OR "google"
```

### Priority 2: AI & ML Engineering / Cloud

These match your cloud and AI expertise.

**Focus shortcut:** Use `/scrape ai engineer`, `/scrape cloud architect`, `/scrape data engineer`, or another role keyword to prioritize this category. To constrain sources, use a preset first, e.g. `/scrape estonia-local cloud architect`.

```
site:linkedin.com/jobs "agentic" USA OR Estonia OR remote
site:linkedin.com/jobs "ai engineer" USA OR Estonia OR remote
site:linkedin.com/jobs "ai agent" USA OR Estonia OR remote
site:linkedin.com/jobs "cloud architect" USA OR Estonia OR remote
site:linkedin.com/jobs "data engineer" USA OR Estonia OR remote
site:linkedin.com/jobs "generative ai" USA OR Estonia OR remote
```

### Priority 3: Technical Consulting / Solutions

Adjacent roles you could pivot into.

**Focus shortcut:** Use `/scrape solutions consultant`, `/scrape technical consultant`, or `/scrape technical account manager` to prioritize this category.

```
site:linkedin.com/jobs "reporting analyst" USA OR Estonia OR remote
site:linkedin.com/jobs "solutions consultant" USA OR Estonia OR remote
site:linkedin.com/jobs "technical account manager" USA OR Estonia OR remote
site:linkedin.com/jobs "technical consultant" USA OR Estonia OR remote
```

### Priority 4: Broader Technical

Wider net for general technical roles.

**Focus shortcut:** Use `/scrape performance marketing`, `/scrape marketing analytics`, `/scrape automation engineer`, or `/scrape developer` to prioritize this category.

```
site:linkedin.com/jobs "digital transformation" USA OR Estonia OR remote
site:linkedin.com/jobs "performance marketing" USA OR Estonia OR remote
site:linkedin.com/jobs "marketing analytics" USA OR Estonia OR remote
site:linkedin.com/jobs "automation" engineer USA OR Estonia OR remote
site:linkedin.com/jobs "developer" USA OR Estonia OR remote
```

### Priority 5: Target Company Direct Web Searches

Direct site filters are split by source-list section so each preset has an exact allowlist. `/scrape broad` still runs all three subgroups.

#### Priority 5a: Google Cloud Partners (`/scrape cloud-partners`)

```
site:mooncascade.com/careers OR site:mooncascade.com/jobs
site:veebiguru.ee "töö" OR site:veebiguru.ee "careers"
site:careers.nortal.com/estonia/ "careers" OR site:careers.nortal.com/estonia/ "jobs"
site:helmes.com "careers" OR site:helmes.com "jobs"
site:mindtitan.com/careers OR site:mindtitan.com/jobs
site:pactum.com/careers OR site:pactum.com/jobs
```

#### Priority 5b: Google Ads Partners (`/scrape ads-partners`)

```
site:eppcdigital.com "careers" OR site:eppcdigital.com "jobs" OR site:eppcdigital.com "work"
site:holini.com "careers" OR site:holini.com "jobs"
site:7p.marketing "careers" OR site:7p.marketing "jobs"
site:mbd.ee "karjäär" OR site:mbd.ee "careers"
```

#### Priority 5c: Estonian Target Companies and Recruiters (`/scrape estonia-targets`)

```
site:bolt.eu/careers
site:wise.com/careers
site:pipedrive.com/en/jobs
site:glia.com/company/careers
site:starship.xyz/careers
site:salv.com/careers
site:scoro.com/careers
site:dataart.com/careers
site:veriff.com/careers OR site:veriff.com/jobs
site:moving2europe.eu
site:relocate.me
site:ittalent.ee
site:humanlab.ee
site:tripod.ee
```

### Priority 6: Remote-First Job Portals

`remote-sources.json` is the executable source-of-truth for this group. Build each WebSearch fallback query from a selected source's `websearch_scope` plus the selected profile terms; then append any user-supplied focus terms and named location/work-mode filters.

**Profiles:**

| Profile | Intent |
|---|---|
| `cloud` | Google Cloud, GCP, Vertex AI, Gemini, generative AI, and AI consulting |
| `marketing` | Google Analytics/GA4, Google Ads, PPC, paid search, SEO/GEO, and marketing analytics |
| `ai` | Generative AI, agentic AI, Vertex AI, AI consulting, and AI strategy |
| `general` | Solutions/technical/cloud consulting, growth strategy, and performance marketing |

**Execution rules:**

1. `/scrape remote-first` searches only sources whose registry tier is `core`.
2. `/scrape remote-first all` adds `secondary` sources; it does not search manual, staffing, discovery, or inactive sources.
3. `/scrape remote-first cloud`, `marketing`, `ai`, or `general` selects that profile. Other focus text is added as a quoted narrowing term rather than replaced with broad defaults.
4. Use a source's `api_*` method when an installed CLI exists; otherwise use its verified `site:` scope. Never invent a `/jobs` or `/careers` suffix.
5. Always verify each listing's work mode and Estonia/U.S./EU/global eligibility from the actual posting; aggregators and WebSearch snippets are not authoritative.

### Priority 7: US Staffing Portals (`/scrape us-staffing`)

**Shortcut:** `/scrape us-staffing` searches only these three major US-based staffing agencies for remote digital marketing and tech roles.

```
site:roberthalf.com "google ads" OR "google analytics" OR "digital marketing" remote
site:creativecircle.com "google ads" OR "digital marketing" remote
site:onwardsearch.com "google ads" OR "digital marketing" remote
```

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

Override the default recency window per run with `--days <1-30>`:

```text
/scrape remote-first ai engineer --country Estonia --remote --days 7
```

## Prompt Examples

Use a source preset when you want to constrain *where* `/scrape` searches. Append ordinary job-focus words to constrain *what* it searches for, then add filters when needed:

```text
/scrape <where> <what> [filters]
```

### Choose where to search

```text
/scrape general-portals cloud architect
/scrape estonia-local data engineer
/scrape cloud-partners ai engineer
/scrape ads-partners marketing analytics
/scrape remote-first technical consultant
/scrape estonia-targets cloud architect
/scrape us-staffing google ads
```

### Add filters

```text
/scrape estonia-local data engineer --city Tallinn
/scrape remote-first cloud architect --country Estonia --remote
/scrape general-portals marketing analyst --country "United States" --remote
/scrape remote-first ai engineer --region Europe --remote --days 7
```

Omit `<where>` to search the normal enabled sources:

```text
/scrape solutions consultant --country Estonia
```
