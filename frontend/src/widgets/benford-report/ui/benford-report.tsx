import {
  BenfordPlot,
  MAD_LABELS,
  chiReading,
  madReading,
  type BenfordDetail,
} from "@/entities/bank"
import { fmt, fmtCount } from "@/shared/lib/format"
import { cn } from "@/shared/lib/utils"
import { Reading } from "@/shared/ui/reading"
import { SectionHead } from "@/shared/ui/section-head"

/**
 * The Benford exhibit: what the digits did, said in a sentence before it is said
 * in figures, because the figures only mean something against Nigrini's limit.
 */
export function BenfordReport({ detail }: { detail: BenfordDetail }) {
  const chi = chiReading(detail)

  return (
    <section className="flex flex-col gap-4">
      <SectionHead aside={`n = ${fmtCount(detail.n)}`}>
        First-digit conformity
      </SectionHead>

      {detail.sufficient ? (
        <>
          <p className="max-w-2xl text-sm leading-relaxed text-pretty">
            {madReading(detail)}
            {chi && <span className="text-muted-foreground"> {chi}</span>}
          </p>

          <BenfordPlot data={detail.distribution} tall />

          <dl className="grid grid-cols-2 gap-x-6 gap-y-5 border-t pt-4 sm:grid-cols-3">
            <Reading label="MAD" emphasis>
              <span className={cn(detail.flagged && "text-destructive")}>
                {fmt(detail.mad)}
              </span>
            </Reading>
            <Reading label="Verdict">
              {MAD_LABELS[detail.mad_label] ?? detail.mad_label}
            </Reading>
            <Reading label="Nigrini limit">{fmt(detail.threshold, 3)}</Reading>
            <Reading label="Bootstrap 95th pct">
              {fmt(detail.calibrated_threshold, 4)}
            </Reading>
            <Reading label="χ²" keepCase>
              {fmt(detail.chi2, 1)}
            </Reading>
            <Reading label="p" keepCase>
              {fmt(detail.chi2_p, 4)}
            </Reading>
          </dl>

          <p className="text-xs text-muted-foreground tabular-nums">
            {fmtCount(detail.n)} usable loan amounts, {detail.dropped} dropped
            as unreadable or non-positive.
          </p>
        </>
      ) : (
        <InsufficientSample detail={detail} />
      )}
    </section>
  )
}

function InsufficientSample({ detail }: { detail: BenfordDetail }) {
  return (
    <div className="flex flex-col gap-2 border-l-2 border-destructive py-1 pl-4">
      <p className="text-sm font-medium text-destructive">
        Not scored on Benford.
      </p>
      <p className="max-w-2xl text-sm leading-relaxed text-pretty text-muted-foreground">
        This bank filed {fmtCount(detail.n)} usable loan amounts — below the
        minimum sample the test needs to tell a real deviation from noise. The
        first-digit reading is withheld rather than reported, so the verdict
        above rests on the other tests alone.
      </p>
    </div>
  )
}
