---
framework_version: 1.2.1
---

# CV Templates and Tailoring Guide

<!-- SETUP: Profile statements and section ordering are personalized by running /setup -->

## Template: LaTeX moderncv (Banking Style)

All CVs use the moderncv LaTeX package with the "banking" style and "blue" color scheme.

**Output file:** `cv/main_<company>_<role>.tex`
**Compile with:** **lualatex** on MiKTeX/TeX Live. pdflatex often fails on modern MiKTeX installs with `fontawesome5` font-expansion errors; lualatex handles the same sources cleanly.
**Master reference:** `cv/main_example.tex` is a structural and presentation reference. It is not an independent factual source; generated CV claims must follow the claim policy below.

### Compile command

```bash
cd cv && lualatex -interaction=nonstopmode main_<company>_<role>.tex
```

Expected output: `Output written on main_<company>_<role>.pdf (... pages, ...)`. A generated CV must be no more than 2 pages and should normally use 2 pages for this senior profile. Never add weak content merely to fill a second page.

## Document Structure

```latex
\documentclass[11pt,a4paper,sans]{moderncv}
\moderncvstyle{banking}
\moderncvcolor{blue}

% Force both first and last name AND section headings to render in moderncv
% blue (color1). Default banking on lualatex+MiKTeX leaves these black, which
% looks inconsistent with the rest of the blue accent scheme.
\renewcommand*{\firstnamestyle}[1]{{\fontsize{34}{36}\bfseries\upshape\color{color1}#1}}
\renewcommand*{\lastnamestyle}[1]{{\fontsize{34}{36}\bfseries\upshape\color{color1}#1}}
\renewcommand*{\sectionstyle}[1]{{\sectionfont\color{color1}#1}}

\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=blue,
    pdftitle={Cory Jaccino - CV},
    pdfpagemode=FullScreen,
}
\usepackage[scale=0.77]{geometry}
\usepackage{import}

% Personal data
\name{Cory}{Jaccino}
\address{Kuressaare, Estonia}{}{}
\phone[mobile]{+372 5854 7237}
\email{cory@coryjaccino.com}
\extrainfo{\href{https://www.linkedin.com/in/coryjaccino}{LinkedIn}}

\begin{document}
\makecvtitle

% 1. Unlabelled, role-specific summary (2-3 sentences)
% 2. Core Competencies
% 3. Professional Experience
% 4. Selected Certifications
% 5. Education
% 6. Languages or selected projects, only when relevant

\end{document}
```

### Color overrides

The three `\renewcommand*` lines in the preamble are required on lualatex+MiKTeX. Without them the firstname, lastname, and section headings render in black even though `\moderncvcolor{blue}` is set, which looks inconsistent with the rest of the blue accent scheme (links, bullet markers, contact icons). The override forces all three to use `color1` (moderncv's accent colour, which becomes blue under `\moderncvcolor{blue}`). Both names render bold; if you prefer the firstname in regular weight, change the firstnamestyle override from `\bfseries` to `\mdseries`. Don't drop the override - on most modern installs the defaults render visibly wrong.

### Spacing inside itemize lists (important)

**Do not place `\vspace{...}` between `\item` entries in an `itemize` list.** Even though the source looks symmetric, this pattern occasionally produces a noticeably oversized gap before a single item: the inter-item `\vspace` creates a paragraph break that interacts unpredictably with the list's internal `\itemsep`, so LaTeX renders one of the gaps wider than the rest. Remove the inter-item `\vspace` and let `itemize` use its native uniform spacing.

```latex
% WRONG - intermittently produces an oversized gap before one bullet
\begin{itemize}
\item \textbf{Foo}: ...
\vspace{1pt}
\item \textbf{Bar}: ...
\vspace{1pt}
\item \textbf{Baz}: ...
\end{itemize}

% RIGHT - uniform spacing using the list's native itemsep
\begin{itemize}
\item \textbf{Foo}: ...
\item \textbf{Bar}: ...
\item \textbf{Baz}: ...
\end{itemize}
```

Two related patterns are fine and should be kept:
- `\vspace{1pt}` immediately after `\section{...}` (between section heading and first item) - this is between the heading and the list, not between list items.
- `\vspace{3pt}` between top-level `\cventry` blocks in Professional Experience or Education - this gives breathing room between roles and renders consistently.

### Section headings must match the CV's language (important)

Section headings such as `\section{Core Competencies}`, `Professional Experience`, `Education`, `Languages`, `Publications`, `Honors and Awards`, `References` (and any others your template defines), plus the `Available upon request.` line under References, are all **literal English text baked into the template** - they do not translate themselves. Whenever the CV language (see `CV language` in the candidate profile) is not English, translate every one of these too, whatever they are, not just the body prose - a CV with a fully localized profile statement and bullets sitting under untouched English section headers reads as sloppy and inconsistent, and it's an easy thing to forget precisely because the prose translation is the obvious, visible part of the job. Worked example for Spanish: `Competencias Clave`, `Experiencia Profesional`, `Educaci\'on`, `Idiomas`, `Publicaciones`, `Distinciones y Premios`, `Referencias`, `Disponibles a solicitud.` The same rule applies for any other target language - check this explicitly during the verification pass.

## Section-by-Section Tailoring

## Factual grounding and claim policy

`01-candidate-profile.md` is the canonical claim inventory for generated CV content. `CLAUDE.md` is a concise profile summary, and `cv/main_example.tex` is a structural and presentation reference; neither independently authorizes a claim.

- **Approved:** A claim in the candidate profile that can be reused or accurately reframed.
- **Needs clarification:** A conflicting, ambiguous, mathematically unclear, or incompletely sourced claim. Do not use it until the user resolves it.
- **In progress:** Professional development that may be identified as ongoing, never as completed.
- **Unsupported:** Do not use it.

Never choose the most impressive version of a conflicting claim. Preserve the conflicting wording in review notes, ask the user which version is current, and use a safe non-numeric approved statement or omit the claim until it is resolved. Existing tailored CVs and cover letters may inform structure or phrasing, never facts.

### Metric integrity checkpoint

Before using a metric, verify its exact value and unit, timeframe, employer and role, category (budget, revenue, savings, opportunity, percentage, or audience), the candidate's relationship to it (managed, generated, influenced, identified, proposed, or reported), and any qualifier. Preserve qualifiers such as `proposed`, `shared responsibility`, `within the first month`, and `opportunity`. Do not add an unverified mechanism to explain a result. If any part is unclear, ask the user; do not guess or use the metric.

### Requirement and gap handling

The CV emphasizes requirements the candidate can prove. Use the posting's exact term only when it is a truthful, natural description of approved evidence. Do not add unsupported keywords, rename stable section headings for a posting keyword, or state ordinary skill gaps in the CV. A material eligibility gap, such as work authorization, clearance, or a mandatory credential, is handled separately and only where appropriate in the cover letter.

### Profile Statement / Elevator Pitch (Best Practice)
This is the most important section to customize. It appears right after `\makecvtitle`.

Write an unlabelled, job-specific summary of 2-3 sentences (about 45-70 words and normally no more than 4 rendered lines). Lead with the most relevant professional identity, add 2-3 approved differentiators, and connect them to the employer's need. Do not use a generic career objective, personality adjectives, an exhaustive skill list, or claims that certifications alone prove production experience.

When the role sits outside your home domain, **lead with the domain-transfer argument** - the one or two sentences connecting your background to their problem (e.g. wave physics to radar signal processing) belong in the profile statement's opening, not buried in the cover letter. It is the strongest card a domain-changer holds; play it first.

The examples below show possible structures only. They are not fact sources and must be rebuilt from approved evidence for every posting.

**For Google Ads / PPC / Digital Marketing roles:**
> 18-year Google Ads and Google Analytics specialist with a proven track record of managing $3M+ yearly budgets, reducing cost-per-install by 73%, and generating over $2B in annual room revenue through global paid search strategy. 14x Google Cloud and 9x Microsoft Azure certified, bringing an AI/automation lens to digital marketing. Experienced across Fortune 500 companies (IHG, Turner) and startups, combining hands-on campaign management with strategic advisory and team mentorship.

**For Google Cloud / AI / ML Engineering roles:**
> Google Cloud-certified mentor who founded a 450+ member ML/AI study group and published certification-preparation content in three languages. Combines cloud training and technical knowledge with 18 years of data-driven digital marketing experience, including analytics and business-impact reporting. Frames technical concepts clearly for diverse audiences.

**For Technical Solutions / Consulting roles:**
> Google Ads and Google Cloud professional who connects technical implementation with business strategy. Brings approved experience in paid-search budgeting, app-install cost reduction, client education, and marketing workflows. Combines Google Cloud, WordPress, Tag Manager, and Looker Studio work with strategic advisory and cross-functional collaboration.

### Core Competencies / Skills Section (Best Practice)
Reorder and emphasize based on the role. Use bold category labels.

List 4-6 compact competency groups in bullet format, tailored to the specific job. Separate professional experience from certifications, project work, familiarity, and in-progress learning. Prefer concrete evidence in Professional Experience over long tool inventories or repeated claims.

Use the posting's own core term in the matching bullet's bold label when it truthfully applies - ATS and skim-reading hiring managers match literally, and "MLOps" in a heading outperforms a paraphrase like "ML Deployment".

### Education
- Label degrees, coursework, exchange programs, and certifications accurately; never present graduate coursework as a graduate degree.
- Keep entries compact. Include dates only when verified in the candidate profile; never guess dates.
- Include 1-3 entries that add relevant qualification or context. Include course descriptions only when verified and directly relevant.

### Professional Experience
- Rewrite bullet points to emphasize aspects most relevant to the target role
- Select visible bullets by relevance to the posting, evidence strength, tenure and scope, uniqueness, recency, career continuity, and the page budget; do not use a fixed count by chronology alone.
- Write each bullet to fit on one rendered line whenever specificity and credibility remain intact. A two-line bullet is an exception for evidence materially weakened by further compression; avoid bullets longer than two lines.
- Use an approved action or responsibility + scope/context + result or purpose. Preserve attribution and qualifiers; do not turn participation, an identified opportunity, or a proposed outcome into ownership or realized savings.
- Keep strong, unused, role-specific alternatives as clearly marked `% ALTERNATIVE:` comments in the generated `.tex` file. They must be approved, non-duplicative, and tailored to the same posting; the strongest bullets remain active by default.
- **Emphasize measurable results** only when the metric passes the metric-integrity checkpoint: "Managed $3M+ budget", "Reduced CPI by 73%", "Generated $2B in annual revenue".

### Handling Employment Gaps (Best Practice)
If there is a gap in your employment history:
- The gap should be explained matter-of-factly if needed
- Describe how professional development continued during the gap
- Frame as deliberate skill-building and career repositioning

### Publications
- Include Google Scholar link if applicable
- Select 3-4 most relevant publications (not always all of them)
- For non-academic roles, keep brief

### Evidence Links
Wherever the CV names a verifiable artifact - a public project, a hackathon entry, a publication - carry its link (`\href`) so a reader can verify the claim in one click. A CV whose strongest claims are checkable reads as more credible everywhere else too.

### Honors and Awards
- Keep format brief, one line each

- Omit references and the "available upon request" line by default. Provide references separately when requested.
- **Do not attach reference letters** - employers typically contact references directly

## Compile-and-Inspect Loop (MANDATORY)

After writing the CV and before presenting to the user, always compile and visually inspect the PDF. Iterate until the layout is clean. Workflow:

1. Run `lualatex -interaction=nonstopmode main_<company>_<role>.tex`
2. Check the output page count: must be exactly 2
3. Read the PDF via the Read tool and visually inspect both pages
4. Check for **orphaned entries**: a `\cventry` title line must never sit alone at the bottom of page 1 with its bullets on page 2

### Fixing common page-break problems

**Problem: entry title on page 1, bullets orphaned to page 2**
Add `\needspace{5\baselineskip}` immediately before the problematic `\cventry`:
```latex
\needspace{5\baselineskip}
\item{\cventry{YEAR--YEAR}{Role Title}{Organization}{Location}{}{...}}
```
Include `\usepackage{needspace}` in the preamble.

**Caveat - use `\needspace` before entries, never before `\section` headings.** A section-level `\needspace` pushes the entire section (heading plus content) to the next page whenever the request does not fit, stranding empty space above and typically *adding* a page instead of saving one. Apply it only to the individual `\cventry` that actually orphans, and only after a compile shows the orphan.

**Problem: one trailing section spills to page 3 (e.g., References alone on page 3)**
Add `\enlargethispage{2-3\baselineskip}` before a late section (e.g., before `\section{Honors and Awards}`) to stretch page 2 by a few lines. This is the standard LaTeX rescue for near-miss overflows.

**Problem: 3 pages with significant content on page 3**
Cut content — do not compress geometry or `\vspace`. See "Relevance-weighted cutting" below for the rule.

**Problem: content finishes early on page 2**
Do not add weak content simply to fill the page. Restore a previously cut item only when it materially strengthens the targeted evidence.

## ATS Parseability

Most employers run CVs through an ATS before a human sees them, and the ATS reads the PDF's embedded **text layer**, not the rendered page. A CV can pass visual inspection and still extract as garbage. After the layout passes the compile-and-inspect loop, verify the text layer:

```bash
cd cv && pdftotext -layout main_<company>_<role>.pdf main_<company>_<role>.txt
```

`pdftotext` comes from [poppler](https://poppler.freedesktop.org/), not the TeX distribution - it is an **optional** dependency. If it is not installed, skip the mechanical check with a warning and rely on the visual PDF read for keyword coverage.

What to check in the extraction:

- **Contact details as literal text.** The stock template's fontawesome contact icons extract as glyph names (`MOBILE-ALT`, `Envelope`) - harmless noise, because the actual address and number are printed beside them. The failure mode is a contact detail carried *only* by an icon or a hyperlink (like the `LinkedIn` link text, whose URL is not in the text layer): invisible to an ATS. The email address must always appear as printed text.
- **No garbled output.** `(cid:NNN)` markers or Unicode replacement characters (`U+FFFD`) mean a font is embedded without a usable Unicode mapping - an ATS sees the same garbage. This shows up with unusual fonts in custom templates, not with the stock moderncv setup under lualatex.
- **Reading order.** The stock banking style is single-column, so extraction order matches visual order. Custom templates (via `/add-template`) with sidebars or multi-column layouts can interleave unrelated lines; if extraction order is scrambled, the user is trading ATS compatibility for looks and should be told.
- **Keyword coverage.** Match the posting's required/preferred terms against the extracted text, in the posting's language. Prefer the posting's exact term over a synonym when it is truthfully applicable - ATS matching is often literal. Never add a keyword the profile does not support.
- **Dates.** Every employment entry must have recognizable dates. Education dates must be recognizable when verified dates exist in the candidate profile; otherwise, their omission is acceptable and must not be guessed.

## Page Budget - Maximum 2 Pages

The generated CV must fit within 2 pages and should normally use 2 pages for this senior profile. Use these flexible limits as a guide:

| Section | Max budget |
|---------|-----------|
| Job-specific summary | Normally 3-4 lines |
| Core Competencies | 4-6 compact groups |
| Anchor role | 2-4 bullets, selected by relevance, tenure, scope, and evidence strength |
| Supporting role | 1-3 bullets |
| Continuity-only role | 1 compact bullet or title/date entry |
| Education | 1-3 compact entries |
| Certifications | Selected credentials or one compact grouped line |
| Optional sections | Include only when they add distinct targeted evidence |

**If in doubt, cut rather than squeeze.** Reducing `\vspace` or geometry scale to force-fit content makes the CV look cramped.

## Relevance-weighted cutting (the right way to shrink a CV)

**Cut by signal, not by section.** Static priority lists ("remove oldest education first, then shorten the earliest role...") are wrong when a relevant "lower-priority" item is competing with an irrelevant "higher-priority" item. An older-role bullet that speaks directly to the posting is worth more than a recent-role bullet that does not.

For every candidate line, score three things:

1. **Relevance to THIS posting** — does the line hit a named tool, keyword, or stated responsibility in the job ad?
2. **Uniqueness** — is it the only place this claim appears, or is it duplicated elsewhere in the CV?
3. **Narrative load** — does the cover letter depend on it? If cutting the line would force you to rewrite a cover-letter paragraph, it is load-bearing.

Cut the lowest-total-score line first, regardless of which section it sits in.

### Practical order of cuts (easiest → last resort)

1. **Redundancy.** If an achievement appears in both Core Competencies AND a role bullet, the Core Competencies version is usually the cleaner cut (the experience bullet is more concrete evidence).
2. **Profile-statement fluff.** A sentence that just restates what Publications or Skills will show. ("Peer-reviewed publications on X..." is already a Publications entry — profile can claim it once and stop.)
3. **Low-relevance experience bullets.** A bullet about work that does not touch posting keywords, wherever it sits. This cuts across sections before touching the structural list.
4. **Low-relevance supporting content.** An older-role bullet that does not speak to the target role. A certification that does not touch the posting's stack. A language entry that can be condensed to one line.
5. **Low-relevance publications.** Keep 1-2 publications that best match the posting. Cut the rest before touching experience bullets.
6. **Last-resort structural cuts.** Oldest education entry, tightening an older role to 2 bullets, collapsing Certifications into a single line. These only happen if the relevance-weighted cuts above have already been exhausted.

### Pitfalls to avoid

- Do not mechanically cut from the bottom of a static section list without checking relevance. "Cut the oldest role first" is wrong if that role is literally about the skill the posting asks for.
- Do not cut the one concrete example the cover letter leans on. Relevance is measured against the cover letter you wrote, not just the job posting — interviewers will have read both.
- Do not cut to fit if the fit is borderline (2.02 pages). Prefer `\enlargethispage{2-3\baselineskip}` on a late section for near-misses; reserve content cuts for genuine overflow (content on page 3 that is more than a single trailing section).

## Default section architecture

Use this order unless the posting supplies a specific reason to change it:

1. Contact header
2. Unlabelled, job-specific summary
3. Core Competencies
4. Professional Experience
5. Selected Certifications
6. Education
7. Languages, when relevant
8. Selected Projects, only when they add evidence not shown in employment

Move Selected Certifications above Professional Experience only when a named credential is a gating requirement. Move Education above Professional Experience only when a verified degree is a central qualifier and stronger than the experience evidence. Omit empty or low-value sections.