export const ui = {
  language: {
    label: "Language",
  },
  theme: {
    switchTitle: "Switch theme (D)",
    toLight: "Switch to light theme",
    toDark: "Switch to dark theme",
  },
  runAudit: {
    running: "Running…",
    run: "Run audit",
  },
  intake: {
    upload: "Upload Report",
    drop: "Drop files here, or click to choose",
    formats: "CSV · XLSX · XML — up to 25 MB each",
    hint: "Choose any number of files, review them below, then send them as one filing. Nothing is examined until you press the button.",
    remove: "remove",
    ready_one: "{{count}} file ready",
    ready_other: "{{count}} files ready",
    sending: "Sending the filing…",
  },
  clearDocket: {
    trigger: "Clear the docket",
    confirm_one: "Clear the docket of {{count}} filing?",
    confirm_other: "Clear the docket of {{count}} filings?",
    body: "Every filing and the files uploaded with it are deleted. The supervisory dataset and the matrix on the front page are untouched.",
    keep: "Keep them",
    clearing: "Clearing…",
  },
  discard: {
    confirm: "Discard",
    keep: "Keep",
    srLabel: "Discard filing {{docket}}",
  },
  search: {
    placeholder: "Find a bank",
  },
  flagged: {
    label: "Flagged only",
  },
  verdictStamp: {
    flagged: "Flagged",
    noFindings: "No findings",
  },
  exceptionCell: {
    noReading: "no reading",
    flagged: "flagged",
    noFinding: "no finding",
    caption: "{{name}} — {{outcome}}, {{score}}",
  },
  benfordPlot: {
    digitTitle:
      "Digit {{digit}}: observed {{observed}}%, expected {{expected}}%",
    observed: "observed",
    benford: "Benford",
    deviationCaption: "deviation in percentage points, per digit",
  },
  filingStatus: {
    flagged_one: "{{count}} flagged",
    flagged_other: "{{count}} flagged",
    noFindings: "No findings",
  },
  dialog: {
    close: "Close",
  },
  toast: {
    auditComplete: "Audit complete",
    flaggedOf: "{{flagged}} of {{total}} banks flagged.",
    noFindingsAcross: "No findings across {{total}} banks.",
    auditFailed: "Audit failed to run",
    filingReceived: "Filing {{docket}} received",
    filingQueued: "It is in the queue. The docket updates as it is examined.",
    filingRejected: "Filing not accepted",
    filingDiscarded: "Filing {{docket}} discarded",
    filingNotDiscarded: "Filing not discarded",
    filingsDiscarded_one: "{{count}} filing discarded",
    filingsDiscarded_other: "{{count}} filings discarded",
    supervisoryUntouched: "The supervisory dataset is untouched.",
    docketNotCleared: "Docket not cleared",
    queryFailed: "Failed to load the data",
  },
}
