import type { BankAudit } from "@/entities/bank"

/** Where a filing stands: two states are in hand, two are settled. */
export type FilingStatus = "queued" | "processing" | "done" | "failed"

/** One remark intake made about a submitted file. */
export type Issue = {
  level: "error" | "warning"
  code: string
  message: string
  file: string | null
  count: number | null
}

export type FilingFile = {
  name: string
  format: string
  size: number
  sha256: string
  role: "register" | "normativ" | "report" | "unknown"
  role_label: string
  rows: number
}

/** A filing as the docket lists it — no per-bank results. */
export type Filing = {
  id: number
  title: string
  status: FilingStatus
  created_at: string
  started_at: string | null
  finished_at: string | null
  files: FilingFile[]
  issues: Issue[]
  /** Tests this filing carried no input for. Not run is not the same as passed. */
  skipped: string[]
  error: string | null
  total_banks: number | null
  suspicious_count: number | null
}

/** A filing with the ranking it produced, once it has been examined. */
export type FilingReport = Filing & {
  results: BankAudit[]
}

export function isOpen(filing: Filing): boolean {
  return filing.status === "queued" || filing.status === "processing"
}
