export type BenfordInfo = {
  n: number
  dropped: number
  mad: number | null
  chi2: number | null
  chi2_p: number | null
  mad_label: string
  sufficient: boolean
  flagged: boolean
  threshold: number | null
  calibrated_threshold: number | null
}

export type BankAudit = {
  bank: string
  suspicious: boolean
  composite: number
  reason: string[]
  benford: BenfordInfo
  detector_flags: Record<string, boolean>
  detector_scores: Record<string, number>
}

export type BenfordDetail = {
  bank: string
  n: number
  dropped: number
  sufficient: boolean
  mad: number | null
  chi2: number | null
  chi2_p: number | null
  mad_label: string
  flagged: boolean
  threshold: number | null
  calibrated_threshold: number | null
  distribution: { digit: number; empirical: number; theoretical: number }[]
}

export type EvidenceRow = Record<string, string | number | boolean>

export type EvidenceBlock = {
  test: string
  title: string
  summary: string
  rows: EvidenceRow[]
}

export type Evidence = {
  bank: string
  reasons: string[]
  blocks: EvidenceBlock[]
}
