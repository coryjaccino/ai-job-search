import { API_URL, apiFetch, countryCode, isFreshAndOpen, toResult, writeError, type JobResult } from "../helpers.js"

export interface SearchOpts {
  query?: string
  countries: string[]
  jobage: number
  page: number
  limit: number
  format: "json" | "table" | "plain"
}

function renderTable(rows: JobResult[]): string {
  if (!rows.length) return "No results."
  const header = "TITLE                                  COMPANY                 ELIGIBILITY               DATE"
  const cell = (value: string, width: number) => value.slice(0, width).padEnd(width)
  return [header, "-".repeat(header.length), ...rows.map((row) => [cell(row.title, 38), cell(row.company, 22), cell(row.location, 25), row.date].join("  "))].join("\n")
}

function renderPlain(rows: JobResult[]): string {
  return rows.length ? rows.map((row) => `${row.title}\n  ${row.company} · ${row.location} · ${row.date}\n  ${row.url}`).join("\n\n") : "No results."
}

export async function runSearch(opts: SearchOpts): Promise<number> {
  const countries = [...new Set(opts.countries.map(countryCode))]
  if (countries.some((country) => !country)) {
    writeError("--country must be a supported name or ISO-3166 alpha-2 code", "BAD_COUNTRY")
    return 1
  }
  try {
    const results = new Map<string, JobResult>()
    let total = 0
    for (const country of countries as string[]) {
      const params = new URLSearchParams({ country, sort: "recent", page: String(opts.page) })
      if (opts.query) params.set("q", opts.query)
      const response = await apiFetch(`${API_URL}?${params}`)
      total += response.totalCount
      for (const job of response.jobs) {
        if (isFreshAndOpen(job, opts.jobage)) results.set(job.guid, toResult(job))
      }
    }
    const rows = [...results.values()].slice(0, opts.limit)
    if (opts.format === "table") process.stdout.write(renderTable(rows) + "\n")
    else if (opts.format === "plain") process.stdout.write(renderPlain(rows) + "\n")
    else process.stdout.write(JSON.stringify({ meta: { count: rows.length, page: opts.page, total }, results: rows }, null, 2) + "\n")
    return 0
  } catch (error) {
    writeError(error instanceof Error ? error.message : String(error), "SEARCH_FAILED")
    return 1
  }
}