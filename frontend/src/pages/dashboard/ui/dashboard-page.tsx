import { testColumns } from "@/entities/bank"
import { RunAuditButton } from "@/features/run-audit"
import { ThemeToggle } from "@/features/theme-toggle"
import { Link } from "@/shared/lib/router"
import { FILINGS_PATH } from "@/shared/lib/routes"
import { AppHeader } from "@/widgets/app-header"
import { AuditLede } from "@/widgets/audit-lede"
import { ExceptionMatrix } from "@/widgets/exception-matrix"

import { useDashboard } from "../model/use-dashboard"

export function DashboardPage() {
  const { meta, rows, loading } = useDashboard()

  const banks = rows ?? []
  const flagged = banks.filter((row) => row.suspicious).length

  return (
    <div className="min-h-svh bg-background text-foreground">
      <AppHeader>
        <Link
          to={FILINGS_PATH}
          className="code mr-1 rounded-sm text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
        >
          Upload Report
        </Link>
        <ThemeToggle />
        <RunAuditButton />
      </AppHeader>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-5 py-8 sm:px-8">
        <AuditLede
          meta={meta}
          total={banks.length}
          flagged={flagged}
          testCount={testColumns(banks).length}
          loading={loading || !rows}
        />

        <ExceptionMatrix rows={banks} loading={loading || !rows} />
      </main>
    </div>
  )
}
