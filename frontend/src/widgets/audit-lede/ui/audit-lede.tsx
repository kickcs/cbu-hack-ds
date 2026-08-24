import type { Meta } from "@/entities/audit"
import { fmtCount } from "@/shared/lib/format"
import { Skeleton } from "@/shared/ui/skeleton"

type Props = {
  meta: Meta | null
  total: number
  flagged: number
  testCount: number
  loading: boolean
}

/**
 * The lede of the report: the finding first, then the provenance of the run that
 * produced it, then the one caveat that can invalidate a Benford reading.
 */
export function AuditLede({ meta, total, flagged, testCount, loading }: Props) {
  if (loading || !meta) {
    return (
      <div className="flex flex-col gap-3 py-2">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-9 w-full max-w-xl" />
        <Skeleton className="h-3 w-72" />
      </div>
    )
  }

  const provenance = [
    `${fmtCount(meta.register_rows)} loan records`,
    `${fmtCount(meta.report_rows)} filed lines`,
    `${fmtCount(meta.normativ_rows)} prudential readings`,
    `${testCount} tests`,
  ].join("  ·  ")

  return (
    <div className="flex flex-col gap-3 py-2">
      <p className="eyebrow">Statistical exception report</p>

      <h1 className="max-w-3xl font-display text-2xl leading-snug font-semibold tracking-tight text-balance sm:text-3xl">
        {flagged > 0 ? (
          <>
            <span className="text-destructive">{flagged}</span> of {total} banks
            failed at least one test.
          </>
        ) : (
          <>All {total} banks passed every test in this run.</>
        )}
      </h1>

      <p className="text-[0.7rem] tracking-wide text-muted-foreground tabular-nums">
        {provenance}
      </p>

      <SampleNotice
        insufficient={meta.insufficient}
        minSample={meta.min_sample}
      />
    </div>
  )
}

function SampleNotice({
  insufficient,
  minSample,
}: {
  insufficient: string[]
  minSample: number
}) {
  if (insufficient.length === 0) {
    return (
      <p className="border-l-2 border-ok py-0.5 pl-3 text-xs text-muted-foreground">
        Every bank clears the n ≥ {minSample} minimum, so the Benford test is
        scored across the board.
      </p>
    )
  }

  return (
    <p className="border-l-2 border-destructive py-0.5 pl-3 text-xs">
      <span className="font-medium text-destructive">
        Sample too small for Benford:
      </span>{" "}
      <span className="text-muted-foreground">
        {insufficient.join(", ")} hold fewer than {minSample} loan records.
        Their first-digit reading is withheld rather than reported.
      </span>
    </p>
  )
}
