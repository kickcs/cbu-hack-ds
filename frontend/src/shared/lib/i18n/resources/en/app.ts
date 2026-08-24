export const app = {
  header: {
    brand: "Bank Supervision",
    tagline: "Central Bank of Uzbekistan",
  },
  matrix: {
    title: "Exception matrix",
    noMatch: "No bank matches the current filters.",
    clearFilters: "Clear filters",
    tests: "Tests",
    bank: "Bank",
    score: "Score",
    mad: "MAD",
    pressToNarrow: "Tests — press to narrow the matrix",
    rankedBy: "Ranked by composite score, worst first",
    fewerThan300: "Fewer than 300 loans — the reading is withheld, not reported.",
  },
  lede: {
    statisticalExceptionReport: "Statistical exception report",
    banks_one: "{{count}} bank",
    banks_other: "{{count}} banks",
    loanRecords_one: "{{total}} loan record",
    loanRecords_other: "{{total}} loan records",
    filedLines_one: "{{total}} filed line",
    filedLines_other: "{{total}} filed lines",
    prudentialReadings_one: "{{total}} prudential reading",
    prudentialReadings_other: "{{total}} prudential readings",
    tests_one: "{{total}} test",
    tests_other: "{{total}} tests",
    failed: "{{flagged}} of {{total}} banks failed at least one test.",
    passed: "All {{banks}} passed every test in this run.",
    sampleOk:
      "Every bank clears the n ≥ {{minSample}} minimum, so the Benford test is scored across the board.",
    sampleTooSmall: "Sample too small for Benford:",
    sampleSmallBody:
      "{{banks}} hold fewer than {{minSample}} loan records. Their first-digit reading is withheld rather than reported.",
  },
  caseFile: {
    title: "Case file",
    navLabel: "Case file",
    allBanks: "All banks",
    firstInRank: "First in rank",
    lastInRank: "Last in rank",
    noFileFor: "No file for “{{bank}}”",
    noFileBody:
      "The latest run holds no bank under that name. Run the audit again, or pick a bank from the exception matrix.",
    backToAllBanks: "Back to all banks",
    detailUnavailable: "Detail unavailable.",
    detailUnavailableBody:
      "The Benford reading and the evidence for this bank could not be loaded. Re-run the audit and open the file again.",
    rank: "Case file · rank {{rank}} of {{total}}",
    findings: "Findings",
    compositeScore: "Composite score",
    loanRecords: "Loan records",
    firedOf: "{{fired}} of {{total}}",
  },
  benford: {
    firstDigitConformity: "First-digit conformity",
    verdict: "Verdict",
    nigriniLimit: "Nigrini limit",
    bootstrap95: "Bootstrap 95th pct",
    usableDropped:
      "{{usable}} usable loan amounts, {{dropped}} dropped as unreadable or non-positive.",
    notScored: "Not scored on Benford.",
    insufficientBody:
      "This bank filed {{total}} usable loan amounts — below the minimum sample the test needs to tell a real deviation from noise. The first-digit reading is withheld rather than reported, so the verdict above rests on the other tests alone.",
  },
  roster: {
    title: "Test roster",
    flaggedOf: "{{fired}} of {{total}} flagged",
    flagged: "Flagged",
    clear: "Clear",
  },
  evidence: {
    title: "Evidence",
    exhibits_one: "{{count}} exhibit",
    exhibits_other: "{{count}} exhibits",
    suspect: "Suspect",
    caption: "{{title}} — {{suspects}} of {{total}} rows marked suspect",
  },
  docket: {
    title: "Docket",
    count_one: "{{count}} filing",
    count_other: "{{count}} filings",
    files_one: "{{count}} file",
    files_other: "{{count}} files",
    remarks_one: "· {{count}} remark",
    remarks_other: "· {{count}} remarks",
    empty:
      "Nothing filed yet. Upload a register, a set of prudential ratios or an aggregate report, and it is examined on its own.",
  },
  filingMasthead: {
    filing: "Filing {{docket}} · filed {{filed}}",
    banksRead: "Banks read",
    flagged: "Flagged",
    files: "Files",
    examinedIn: "Examined in",
    bankScope_one: "{{count}} bank",
    bankScope_other: "{{count}} banks",
    clean:
      "Nothing in this filing crossed a threshold. {{scope}} were read and every test they carried input for came back clean.",
    flaggedSentence:
      "{{flagged}} of {{scope}} in this filing crossed at least one threshold. They are ranked below, worst first.",
    rows_one: "{{count}} row",
    rows_other: "{{count}} rows",
  },
  filingNotes: {
    onData: "{{count}} on the data",
    testsSkipped_one: "{{count}} test skipped",
    testsSkipped_other: "{{count}} tests skipped",
    remarks: "Remarks",
    error: "Error",
    warning: "Warning",
    skippedLine_one:
      "One test was not run: this filing carried no input for {{names}}.",
    skippedLine_other:
      "{{count}} tests were not run: this filing carried no input for {{names}}.",
    skippedCoda: "A test that did not run is not a test that passed.",
    skippedPrefix: "Skipped · {{codes}}",
  },
  filings: {
    uploadReport: "Upload Report",
    navLabel: "Upload report",
    supervisoryDataset: "Supervisory dataset",
    title: "File a report for examination",
    intro:
      "Each filing is queued, examined on its own and kept apart from every other. Send a loan register, a set of prudential ratios, an aggregate report — or all three at once, and the tests that have input will run.",
  },
  filingReport: {
    navLabel: "Filing",
    docket: "Docket",
    caption: "Findings in filing {{docket}}",
    stillOpen:
      "The findings appear here as soon as the examination finishes.",
    filing: "Filing {{docket}}",
    noSuch: "No such filing",
    noSuchBody:
      "Nothing is on the docket under that number. It may have been discarded. Upload the report again to have it examined.",
    backToDocket: "Back to the docket",
  },
}
