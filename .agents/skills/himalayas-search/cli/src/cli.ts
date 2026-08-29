#!/usr/bin/env bun
import { runSearch, type SearchOpts } from "./commands/search.js"
import { writeError } from "./helpers.js"

type Flags = Record<string, string | boolean | string[]> & { _: string[] }

function parseFlags(argv: string[]): Flags {
  const flags: Flags = { _: [] }
  const aliases: Record<string, string> = { q: "query", n: "limit" }
  for (let index = 0; index < argv.length; index++) {
    const arg = argv[index]
    if (!arg.startsWith("-")) { flags._.push(arg); continue }
    const key = aliases[arg.replace(/^-+/, "")] ?? arg.replace(/^-+/, "")
    const value = argv[index + 1]
    if (!value || value.startsWith("-")) { flags[key] = true; continue }
    index++
    if (key === "country") {
      const current = flags.country
      flags.country = [...(Array.isArray(current) ? current : current ? [String(current)] : []), value]
    } else flags[key] = value
  }
  return flags
}

const HELP = `himalayas-search — country-qualified remote-job search via Himalayas' public API

USAGE
  bun run src/cli.ts search --country <name|ISO> [flags]

SEARCH FLAGS
  --country <name|ISO>     REQUIRED; repeat for an OR list, e.g. Estonia / EE or United States / US.
  --query, -q <text>      Server-side keyword search.
  --jobage <days>         Maximum posting age; checked against API publication date.
  --page <n>              API result page, default 1.
  --limit, -n <n>         Maximum merged results, default 20.
  --format <fmt>          json (default), table, or plain.
`

function integer(flags: Flags, name: string, fallback: number): number | null {
  if (flags[name] === undefined) return fallback
  const value = Number.parseInt(String(flags[name]), 10)
  if (!Number.isFinite(value) || value < 0) { writeError(`--${name} must be a non-negative integer`, "BAD_ARG"); return null }
  return value
}

async function main(): Promise<number> {
  const flags = parseFlags(process.argv.slice(2))
  const command = flags._[0]
  if (!command || flags.help || flags.h) { process.stdout.write(HELP); return command ? 0 : 1 }
  if (command === "search") {
    const countries = Array.isArray(flags.country) ? flags.country : flags.country ? [String(flags.country)] : []
    if (!countries.length) { writeError("the --country flag is required; use Estonia/EE and/or United States/US", "NO_COUNTRY"); return 1 }
    const jobage = integer(flags, "jobage", 9999), page = integer(flags, "page", 1), limit = integer(flags, "limit", 20)
    if (jobage === null || page === null || limit === null || page < 1 || limit < 1) { if (page !== null && limit !== null && (page < 1 || limit < 1)) writeError("--page and --limit must be at least 1", "BAD_ARG"); return 1 }
    const format = ["json", "table", "plain"].includes(String(flags.format ?? "json")) ? String(flags.format ?? "json") as SearchOpts["format"] : "json"
    return runSearch({ query: typeof flags.query === "string" ? flags.query : undefined, countries, jobage, page, limit, format })
  }
  writeError(`Unknown command "${command}"`, "BAD_CMD")
  return 1
}

main().then((code) => process.exit(code)).catch((error) => { writeError(error instanceof Error ? error.message : String(error), "INTERNAL_ERROR"); process.exit(1) })