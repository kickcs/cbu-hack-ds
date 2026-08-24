export type TestLabel = {
  /** Full name, used in the case file and in tooltips. */
  name: string
  /** Column head in the exception matrix — must survive a 3ch column. */
  code: string
  /** What the test looks for, one line. */
  about: string
}

/**
 * Column order of the exception matrix, coarsest test first. Data may carry
 * tests that are not listed here (the closed dataset enables more detectors),
 * so anything unknown is humanised by `testLabel` and appended.
 */
export const TEST_ORDER = [
  "benford",
  "threshold",
  "rounding",
  "arithmetic",
  "balance",
  "discontinuity",
  "window_dressing",
  "last_digit",
] as const

const TESTS: Record<string, TestLabel> = {
  benford: {
    name: "Benford's law",
    code: "BEN",
    about:
      "First digits of loan amounts against the expected 30.1 / 17.6 / 12.5 % curve",
  },
  threshold: {
    name: "K1 limit",
    code: "K1",
    about:
      "Capital adequacy readings clustering just above the regulatory floor",
  },
  rounding: {
    name: "Round figures",
    code: "RND",
    about: "Reported amounts ending in an implausible run of zeros",
  },
  arithmetic: {
    name: "Assets footing",
    code: "FTG",
    about: "Reported assets total against the sum of its components",
  },
  balance: {
    name: "Balance identity",
    code: "BAL",
    about: "Assets against liabilities — the accounting identity",
  },
  discontinuity: {
    name: "Series break",
    code: "BRK",
    about: "Month-to-month jumps inside the reporting year",
  },
  window_dressing: {
    name: "Window dressing",
    code: "WDR",
    about: "Balance-sheet growth concentrated in the closing period",
  },
  last_digit: {
    name: "Last digit",
    code: "LDG",
    about: "Final digits of loan amounts against a uniform distribution",
  },
}

function humanise(key: string): string {
  const words = key.replace(/_/g, " ")
  return words.charAt(0).toUpperCase() + words.slice(1)
}

export function testLabel(key: string): TestLabel {
  return (
    TESTS[key] ?? {
      name: humanise(key),
      code: key.slice(0, 3).toUpperCase(),
      about: "Additional statistical test",
    }
  )
}

export const MAD_LABELS: Record<string, string> = {
  close: "Close conformity",
  acceptable: "Acceptable",
  marginally_acceptable: "Marginal",
  nonconformity: "Nonconformity",
}
