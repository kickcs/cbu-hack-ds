export const common = {
  tests: {
    benford: {
      name: "Benford's law",
      about:
        "First digits of loan amounts against the expected 30.1 / 17.6 / 12.5 % curve",
    },
    threshold: {
      name: "K1 limit",
      about:
        "Capital adequacy readings clustering just above the regulatory floor",
    },
    rounding: {
      name: "Round figures",
      about: "Reported amounts ending in an implausible run of zeros",
    },
    arithmetic: {
      name: "Assets footing",
      about: "Reported assets total against the sum of its components",
    },
    balance: {
      name: "Balance identity",
      about: "Assets against liabilities — the accounting identity",
    },
    discontinuity: {
      name: "Series break",
      about: "Month-to-month jumps inside the reporting year",
    },
    windowDressing: {
      name: "Window dressing",
      about: "Balance-sheet growth concentrated in the closing period",
    },
    lastDigit: {
      name: "Last digit",
      about: "Final digits of loan amounts against a uniform distribution",
    },
    unknownAbout: "Additional statistical test",
  },
  mad: {
    close: "Close conformity",
    acceptable: "Acceptable",
    marginally_acceptable: "Marginal",
    nonconformity: "Nonconformity",
  },
  status: {
    queued: "In queue",
    processing: "Examining",
    done: "Examined",
    failed: "Returned",
  },
  statusNote: {
    queued: "Waiting for the examiner",
    processing: "Tests are running",
    done: "Findings are ready",
    failed: "Nothing could be examined",
  },
  time: {
    underSecond: "under a second",
  },
  evidence: {
    cols: {
      period: "period",
      indicator: "indicator",
      value: "value",
      trailing_zeros: "zeros",
      transition: "months",
      before: "before",
      after: "after",
      growth: "growth",
      limit: "limit",
      margin: "margin",
      digit: "digit",
      observed: "observed",
      expected: "expected",
      deviation: "deviation",
      share: "share",
      count: "count",
      expected_count: "expected",
      total_assets: "assets",
      total_liabilities: "liabilities",
      sum_of_parts: "sum of parts",
      gap: "gap",
      gap_share: "gap %",
    },
    yes: "yes",
      blocks: {
        benford: {
          title: "Departure from Benford's law",
          summary:
            "Digit {{digit}} leads {{observed}} of amounts instead of {{expected}}, a deviation of {{deviation}}.",
        },
        threshold: {
          title: "Clustering just above the K1 limit",
          summary:
            "{{flagged}} of {{total}} K1 readings sit in a narrow band just above the regulatory limit (limit, limit+{{band}}].",
        },
        rounding: {
          title: "Implausibly round figures",
          summary: "{{count}} reported figures end in {{zeros}} or more zeros.",
        },
        arithmetic: {
          title: "Total assets do not foot",
          summary:
            "The reported assets total does not match the sum of its components.",
        },
        balance: {
          title: "Assets do not equal liabilities",
          summary:
            "Reported assets differ from reported liabilities, breaking the accounting identity.",
        },
        discontinuity: {
          title: "Break in the reported series",
          summary: "Total assets jump between consecutive months.",
        },
        window_dressing: {
          title: "Spike in the closing period",
          summary: "Total assets grow abnormally into the year end.",
        },
        last_digit: {
          title: "Last digit is not uniform",
          summary:
            "chi2 = {{chi2}}, p = {{p}} against a uniform last digit across {{n}} loan amounts in the register.",
        },
      },
  },

  verdict: {
    clean: "Nothing in this bank's filings tripped a test. All {{count}} ran and returned no finding.",
    fired: "{{fired}} of {{count}} tests returned a finding: {{names}}.",
    madFlagged:
      "A mean absolute deviation of {{mad}} sits above Nigrini's {{limit}} limit, so the first digits read as {{label}} — the spread is unlikely to have come from ordinary lending.",
    madClean:
      "A mean absolute deviation of {{mad}} stays under Nigrini's {{limit}} limit, so the first digits track the law at {{label}}.",
    chiReject: "χ² rejects the fit at the {{level}}% level (p = {{p}}).",
    chiAccept: "χ² does not reject the fit (p = {{p}}).",
  },
  errors: {
    generic: "Something went wrong",
    network: "The API is not answering — check that it is running on :8000",
    http: "HTTP {{status}} {{statusText}}",
  },
}
