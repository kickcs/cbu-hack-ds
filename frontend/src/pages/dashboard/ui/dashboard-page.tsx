import { testColumns } from "@/entities/bank"
import { RunAuditButton } from "@/features/run-audit"
import { ThemeToggle } from "@/features/theme-toggle"
import { AppHeader } from "@/widgets/app-header"
import { AuditLede } from "@/widgets/audit-lede"
import { BankDossier } from "@/widgets/bank-dossier"
import { ExceptionMatrix } from "@/widgets/exception-matrix"

import { useDashboard } from "../model/use-dashboard"

export function DashboardPage() {
  const { meta, rows, loading, selected, select, closeSelected } = useDashboard()

  const banks = rows ?? []
  const flagged = banks.filter((row) => row.suspicious).length

  return (
    <div className="min-h-svh bg-background text-foreground">
      <AppHeader>
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

        <ExceptionMatrix
          rows={banks}
          loading={loading || !rows}
          onSelect={select}
        />
      </main>

      <BankDossier audit={selected} onClose={closeSelected} />
    </div>
  )
}
