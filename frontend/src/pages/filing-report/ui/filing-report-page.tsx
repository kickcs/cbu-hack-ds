import { useQuery } from "@tanstack/react-query"
import { ChevronLeftIcon } from "lucide-react"

import { docketNo, filingQuery, isOpen } from "@/entities/submission"
import { DiscardFilingButton } from "@/features/clear-docket"
import { ThemeToggle } from "@/features/theme-toggle"
import { Link } from "@/shared/lib/router"
import { FILINGS_PATH } from "@/shared/lib/routes"
import { Skeleton } from "@/shared/ui/skeleton"
import { AppHeader } from "@/widgets/app-header"
import { ExceptionMatrix } from "@/widgets/exception-matrix"
import { FilingMasthead } from "@/widgets/filing-masthead"
import { FilingNotes } from "@/widgets/filing-notes"

/**
 * One filing, examined on its own. The ranking here is drawn only from the
 * files uploaded with it; bank rows open the supervisory case file for that
 * bank, the same way they do on the dashboard.
 */
export function FilingReportPage({ id }: { id: number }) {
  const { data: filing, isPending, isError } = useQuery(filingQuery(id))

  return (
    <div className="min-h-svh bg-background text-foreground">
      <AppHeader>
        <ThemeToggle />
      </AppHeader>

      <nav
        aria-label="Filing"
        className="sticky top-14 z-10 border-b bg-background/90 backdrop-blur"
      >
        <div className="mx-auto flex h-11 max-w-5xl items-center justify-between gap-4 px-5 sm:px-8">
          <Link
            to={FILINGS_PATH}
            className="code flex items-center gap-1 rounded-sm text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
          >
            <ChevronLeftIcon className="size-3" />
            Docket
          </Link>
          {filing && <DiscardFilingButton id={filing.id} />}
        </div>
      </nav>

      <main className="mx-auto flex max-w-5xl flex-col gap-10 px-5 py-8 sm:px-8">
        {isPending && <LoadingFiling />}

        {isError && <NoFiling id={id} />}

        {filing && (
          <>
            <FilingMasthead filing={filing} />

            <FilingNotes issues={filing.issues} skipped={filing.skipped} />

            {isOpen(filing) && <StillOpen />}

            {filing.status === "done" && filing.results.length > 0 && (
              <ExceptionMatrix
                rows={filing.results}
                loading={false}
                caption={`Findings in filing ${docketNo(filing.id)}`}
              />
            )}
          </>
        )}
      </main>
    </div>
  )
}

/** The page polls itself, so this is a placeholder rather than an instruction. */
function StillOpen() {
  return (
    <section className="flex flex-col gap-3">
      <p className="border-l-2 py-1 pl-4 text-sm text-muted-foreground">
        The findings appear here as soon as the examination finishes.
      </p>
      <Skeleton className="h-48 w-full" />
    </section>
  )
}

function NoFiling({ id }: { id: number }) {
  return (
    <section className="flex flex-col items-start gap-4 border-l-2 pl-5">
      <p className="eyebrow">Filing {docketNo(id)}</p>
      <h1 className="font-display text-2xl font-semibold tracking-tight">
        No such filing
      </h1>
      <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
        Nothing is on the docket under that number. It may have been discarded.
        Upload the report again to have it examined.
      </p>
      <Link
        to={FILINGS_PATH}
        className="code rounded-sm text-foreground underline underline-offset-4 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
      >
        Back to the docket
      </Link>
    </section>
  )
}

function LoadingFiling() {
  return (
    <div className="flex flex-col gap-6">
      <Skeleton className="h-3 w-40" />
      <Skeleton className="h-10 w-72 max-w-full" />
      <Skeleton className="h-4 w-full max-w-xl" />
      <Skeleton className="h-16 w-full max-w-lg" />
    </div>
  )
}
