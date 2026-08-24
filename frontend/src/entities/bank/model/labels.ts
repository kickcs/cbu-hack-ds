import i18n from "@/shared/lib/i18n"

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

const TEST_CODES: Record<string, string> = {
  benford: "BEN",
  threshold: "K1",
  rounding: "RND",
  arithmetic: "FTG",
  balance: "BAL",
  discontinuity: "BRK",
  window_dressing: "WDR",
  last_digit: "LDG",
}

function humanise(key: string): string {
  const words = key.replace(/_/g, " ")
  return words.charAt(0).toUpperCase() + words.slice(1)
}

export function testLabel(key: string): TestLabel {
  const code = TEST_CODES[key]
  if (!code) {
    return {
      name: humanise(key),
      code: key.slice(0, 3).toUpperCase(),
      about: i18n.t("common:tests.unknownAbout"),
    }
  }

  return {
    name: i18n.t(`common:tests.${key}.name`),
    code,
    about: i18n.t(`common:tests.${key}.about`),
  }
}

/** Human label for a MAD band — null when the band is not one we know. */
export function madLabel(key: string): string | null {
  const value = i18n.t(`common:mad.${key}`)
  return value === `common:mad.${key}` ? null : value
}
