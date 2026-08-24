import { TEST_ORDER } from "../model/labels"
import type { BankAudit } from "../model/types"

export const BENFORD_TEST = "benford"

export type TestCell = {
  test: string
  flagged: boolean
  /** 0…1 intensity used to ink the matrix cell. */
  intensity: number
  /** Raw score as the backend reports it, or the MAD for Benford. */
  score: number | null
}

/**
 * Matrix columns come from the data, not from a fixed list: the closed dataset
 * may enable detectors this build has never seen. Known tests keep their
 * curated order, anything new is appended alphabetically.
 */
export function testColumns(rows: BankAudit[]): string[] {
  const found = new Set<string>([BENFORD_TEST])
  for (const row of rows) {
    for (const key of Object.keys(row.detector_flags)) found.add(key)
  }

  const known = TEST_ORDER.filter((key) => found.has(key))
  const extra = [...found]
    .filter((key) => !TEST_ORDER.includes(key as (typeof TEST_ORDER)[number]))
    .sort()

  return [...known, ...extra]
}

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value))
}

export function testCell(audit: BankAudit, test: string): TestCell {
  if (test === BENFORD_TEST) {
    const { mad, threshold, flagged } = audit.benford
    // Intensity reads against Nigrini's limit: a full cell sits at the limit.
    const intensity = mad !== null && threshold ? clamp01(mad / threshold) : 0
    return { test, flagged, intensity, score: mad }
  }

  const score = audit.detector_scores[test] ?? null
  return {
    test,
    flagged: audit.detector_flags[test] ?? false,
    intensity: clamp01(score ?? 0),
    score,
  }
}

export function testCells(audit: BankAudit, tests: string[]): TestCell[] {
  return tests.map((test) => testCell(audit, test))
}
