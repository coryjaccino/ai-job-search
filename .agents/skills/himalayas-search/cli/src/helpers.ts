export const API_URL = "https://himalayas.app/jobs/api/search"

export interface ApiJob {
  guid: string
  title: string
  companyName: string
  employmentType: string | null
  seniority: string[]
  locationRestrictions: Array<string | { alpha2?: string; name?: string; slug?: string }>
  timezoneRestrictions: number[]
  description: string
  pubDate: number
  expiryDate: number | null
  applicationLink: string
  categories: string[]
}

export interface ApiResponse {
  totalCount: number
  jobs: ApiJob[]
}

export interface JobResult {
  id: string
  title: string
  company: string
  location: string
  date: string
  url: string
  employmentType: string | null
  seniority: string[]
  locationRestrictions: string[]
  timezoneRestrictions: number[]
  expiryDate: string | null
  categories: string[]
  description: string
}

export function writeError(error: string, code: string): void {
  process.stderr.write(JSON.stringify({ error, code }) + "\n")
}

export async function apiFetch(url: string): Promise<ApiResponse> {
  const response = await fetch(url, {
    headers: { Accept: "application/json", "User-Agent": "ai-job-search/1.0 (personal job search)" },
    signal: AbortSignal.timeout(20_000),
  })
  if (!response.ok) throw new Error(`Request failed: ${response.status} ${response.statusText}`)
  return response.json() as Promise<ApiResponse>
}

export function restrictionNames(restrictions: ApiJob["locationRestrictions"]): string[] {
  return restrictions.map((restriction) => {
    if (typeof restriction === "string") return restriction
    return restriction.name ?? restriction.alpha2 ?? restriction.slug ?? "Unknown"
  })
}

export function toResult(job: ApiJob): JobResult {
  const restrictions = restrictionNames(job.locationRestrictions)
  return {
    id: job.guid,
    title: job.title,
    company: job.companyName,
    location: restrictions.length ? restrictions.join(", ") : "Worldwide",
    date: new Date(job.pubDate * 1000).toISOString().slice(0, 10),
    url: job.applicationLink || job.guid,
    employmentType: job.employmentType,
    seniority: job.seniority ?? [],
    locationRestrictions: restrictions,
    timezoneRestrictions: job.timezoneRestrictions ?? [],
    expiryDate: job.expiryDate ? new Date(job.expiryDate * 1000).toISOString().slice(0, 10) : null,
    categories: job.categories ?? [],
    description: job.description ?? "",
  }
}

export function isFreshAndOpen(job: ApiJob, jobage: number, now = Date.now()): boolean {
  if (job.expiryDate && job.expiryDate * 1000 < now) return false
  return !jobage || jobage >= 9999 || now - job.pubDate * 1000 <= jobage * 86_400_000
}

export function countryCode(input: string): string | null {
  const normalized = input.trim().toLowerCase()
  const aliases: Record<string, string> = {
    ee: "EE", estonia: "EE", us: "US", usa: "US", "united states": "US", "united states of america": "US",
  }
  return aliases[normalized] ?? (normalized.length === 2 ? normalized.toUpperCase() : null)
}