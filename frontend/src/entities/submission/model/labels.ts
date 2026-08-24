import type { FilingStatus } from "./types"

/** The word stamped on a filing at each stage, in the clerk's own vocabulary. */
export const STATUS_LABELS: Record<FilingStatus, string> = {
  queued: "In queue",
  processing: "Examining",
  done: "Examined",
  failed: "Returned",
}

/** What the auditor should read into that word. */
export const STATUS_NOTES: Record<FilingStatus, string> = {
  queued: "Waiting for the examiner",
  processing: "Tests are running",
  done: "Findings are ready",
  failed: "Nothing could be examined",
}

/** Docket number: the id, set as a clerk would write it. */
export function docketNo(id: number): string {
  return id.toString().padStart(3, "0")
}

const STAMP = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
})

/** When the filing came in, in the reader's own zone — the date stamp on it. */
export function filedAt(iso: string): string {
  const at = new Date(iso)
  return Number.isNaN(at.valueOf()) ? "—" : STAMP.format(at)
}

/** How long the examination took, once both ends of it are known. */
export function tookFor(
  started: string | null,
  finished: string | null
): string | null {
  if (!started || !finished) return null
  const ms = new Date(finished).valueOf() - new Date(started).valueOf()
  if (Number.isNaN(ms) || ms < 0) return null
  return ms < 1_000 ? "under a second" : `${(ms / 1_000).toFixed(1)}s`
}
