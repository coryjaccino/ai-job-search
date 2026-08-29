import { describe, expect, test } from "bun:test"
import { countryCode, isFreshAndOpen, restrictionNames, toResult, type ApiJob } from "../src/helpers.js"

const job: ApiJob = { guid: "https://himalayas.app/companies/example/jobs/role", title: "Google Analytics Specialist", companyName: "Example", employmentType: "Full Time", seniority: ["Senior"], locationRestrictions: ["Estonia"], timezoneRestrictions: [2], description: "Description", pubDate: 1_700_000_000, expiryDate: 1_900_000_000, applicationLink: "https://himalayas.app/companies/example/jobs/role", categories: ["Marketing"] }

describe("Himalayas result helpers", () => {
  test("normalizes country aliases", () => { expect(countryCode("Estonia")).toBe("EE"); expect(countryCode("United States")).toBe("US"); expect(countryCode("bad country")).toBeNull() })
  test("preserves structured eligibility in results", () => { expect(toResult(job).location).toBe("Estonia"); expect(restrictionNames([{ alpha2: "EE", name: "Estonia" }])).toEqual(["Estonia"]) })
  test("rejects expired and stale jobs", () => { expect(isFreshAndOpen({ ...job, expiryDate: 1 }, 14, 1_800_000_000)).toBeFalse(); expect(isFreshAndOpen({ ...job, pubDate: 1 }, 14, 1_800_000_000)).toBeFalse() })
})