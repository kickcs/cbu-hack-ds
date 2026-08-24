export const DASHBOARD_PATH = "/"
export const FILINGS_PATH = "/filings"

export function filingPath(id: number): string {
  return `/filings/${id}`
}

/** The filing a docket path points at, or null when the path is not one. */
export function filingIdFromPath(path: string): number | null {
  const match = /^\/filings\/(\d+)\/?$/.exec(path)
  return match ? Number(match[1]) : null
}

export function bankPath(bank: string): string {
  return `/bank/${encodeURIComponent(bank)}`
}

/** The bank a case-file path points at, or null when the path is not one. */
export function bankFromPath(path: string): string | null {
  const match = /^\/bank\/([^/]+)\/?$/.exec(path)
  if (!match) return null
  try {
    return decodeURIComponent(match[1])
  } catch {
    return null
  }
}
