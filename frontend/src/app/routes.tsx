import { BankCaseFilePage } from "@/pages/bank-case-file"
import { DashboardPage } from "@/pages/dashboard"
import { FilingReportPage } from "@/pages/filing-report"
import { FilingsPage } from "@/pages/filings"
import { usePath } from "@/shared/lib/router"
import {
  bankFromPath,
  filingIdFromPath,
  FILINGS_PATH,
} from "@/shared/lib/routes"

/** The ranked matrix, one bank's case file, the intake docket, one filing. */
export function AppRoutes() {
  const path = usePath()

  const filing = filingIdFromPath(path)
  // Keyed so stepping between filings remounts the report instead of blending them.
  if (filing !== null) return <FilingReportPage key={filing} id={filing} />

  if (path === FILINGS_PATH || path === `${FILINGS_PATH}/`)
    return <FilingsPage />

  const bank = bankFromPath(path)
  return bank ? <BankCaseFilePage key={bank} bank={bank} /> : <DashboardPage />
}
