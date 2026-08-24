import { useQuery } from "@tanstack/react-query"
import { ChevronLeftIcon } from "lucide-react"

import { filingsQuery } from "@/entities/submission"
import { IntakeWindow } from "@/features/file-a-report"
import { ThemeToggle } from "@/features/theme-toggle"
import { Link } from "@/shared/lib/router"
import { DASHBOARD_PATH } from "@/shared/lib/routes"
import { AppHeader } from "@/widgets/app-header"
import { DocketList } from "@/widgets/docket-list"

/**
 * The intake desk: hand a filing in at the top, watch it move down the docket
 * below. Nothing filed here touches the supervisory dataset.
 */
export function FilingsPage() {
  const { data, isPending } = useQuery(filingsQuery())

  return (
    <div className="min-h-svh bg-background text-foreground">
      <AppHeader>
        <ThemeToggle />
      </AppHeader>

      <nav
        aria-label="Upload report"
        className="sticky top-14 z-10 border-b bg-background/90 backdrop-blur"
      >
        <div className="mx-auto flex h-11 max-w-4xl items-center px-5 sm:px-8">
          <Link
            to={DASHBOARD_PATH}
            className="code flex items-center gap-1 rounded-sm text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
          >
            <ChevronLeftIcon className="size-3" />
            Supervisory dataset
          </Link>
        </div>
      </nav>

      <main className="mx-auto flex max-w-4xl flex-col gap-10 px-5 py-8 sm:px-8">
        <header className="flex flex-col gap-3 border-l-2 pl-5">
          <p className="eyebrow">Upload Report</p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
            File a report for examination
          </h1>
          <p className="max-w-2xl text-base leading-relaxed text-pretty">
            Each filing is queued, examined on its own and kept apart from every
            other. Send a loan register, a set of prudential ratios, an
            aggregate report — or all three at once, and the tests that have
            input will run.
          </p>
        </header>

        <IntakeWindow />

        <DocketList filings={data ?? []} loading={isPending} />
      </main>
    </div>
  )
}
