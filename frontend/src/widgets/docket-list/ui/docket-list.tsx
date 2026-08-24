import {
  DocketRule,
  FilingStatusMark,
  docketNo,
  filedAt,
  type Filing,
} from "@/entities/submission"
import { ClearDocketButton, DiscardFilingButton } from "@/features/clear-docket"
import { Link } from "@/shared/lib/router"
import { filingPath } from "@/shared/lib/routes"
import { cn } from "@/shared/lib/utils"
import { SectionHead } from "@/shared/ui/section-head"
import { Skeleton } from "@/shared/ui/skeleton"

type Props = {
  filings: Filing[]
  loading: boolean
}

/**
 * The docket: every filing handed in, newest at the top, each with the mark in
 * its margin saying how far it has got. Rows stay in place as a filing moves
 * from queue to verdict, so the auditor can watch one without losing the list.
 */
export function DocketList({ filings, loading }: Props) {
  return (
    <section className="flex flex-col gap-3">
      <SectionHead
        aside={
          filings.length > 0
            ? `${filings.length} ${filings.length === 1 ? "filing" : "filings"}`
            : undefined
        }
      >
        Docket
      </SectionHead>

      {loading && <LoadingRows />}

      {!loading && filings.length === 0 && <EmptyDocket />}

      {!loading && filings.length > 0 && (
        <>
          <ul className="flex flex-col">
            {filings.map((filing, i) => (
              <DocketRow key={filing.id} filing={filing} index={i} />
            ))}
          </ul>
          <div className="flex justify-end">
            <ClearDocketButton count={filings.length} />
          </div>
        </>
      )}
    </section>
  )
}

function DocketRow({ filing, index }: { filing: Filing; index: number }) {
  const flagged = filing.suspicious_count ?? 0
  const settled = filing.status === "done" || filing.status === "failed"

  return (
    <li
      style={{ animationDelay: `${Math.min(index, 12) * 30}ms` }}
      className="row-in group flex items-stretch gap-3 border-b border-border/60 py-2.5 last:border-b-0"
    >
      <DocketRule status={filing.status} flagged={flagged > 0} />

      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        <div className="flex items-baseline gap-2">
          <span className="code shrink-0 text-muted-foreground">
            {docketNo(filing.id)}
          </span>
          {settled ? (
            <Link
              to={filingPath(filing.id)}
              className="truncate rounded-sm text-sm font-medium hover:underline focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
            >
              {filing.title}
            </Link>
          ) : (
            <span className="truncate text-sm font-medium text-muted-foreground">
              {filing.title}
            </span>
          )}
        </div>

        <p className="truncate text-xs text-muted-foreground">
          {filedAt(filing.created_at)} ·{" "}
          {filing.files.length === 1
            ? "1 file"
            : `${filing.files.length} files`}
          {filing.status === "done" &&
            filing.issues.length > 0 &&
            ` · ${filing.issues.length} ${filing.issues.length === 1 ? "remark" : "remarks"}`}
        </p>

        {/* Why a filing came back is the whole content of the row, not a footnote to it. */}
        {filing.status === "failed" && filing.error && (
          <p className="mt-0.5 line-clamp-2 text-xs leading-relaxed text-destructive">
            {filing.error}
          </p>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-2 self-center">
        <FilingStatusMark
          status={filing.status}
          findings={filing.suspicious_count}
        />
        <span
          className={cn(
            // The row is not a control panel until the auditor looks at it.
            "transition-opacity group-hover:opacity-100 focus-within:opacity-100 sm:opacity-0"
          )}
        >
          <DiscardFilingButton id={filing.id} />
        </span>
      </div>
    </li>
  )
}

function EmptyDocket() {
  return (
    <p className="border-l-2 py-1 pl-4 text-sm text-muted-foreground">
      Nothing filed yet. Upload a register, a set of prudential ratios or an
      aggregate report, and it is examined on its own.
    </p>
  )
}

function LoadingRows() {
  return (
    <div className="flex flex-col gap-3 py-1">
      {Array.from({ length: 3 }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full" />
      ))}
    </div>
  )
}
