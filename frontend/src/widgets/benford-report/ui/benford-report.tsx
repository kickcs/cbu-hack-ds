import { useTranslation } from "react-i18next"

import {
  BenfordPlot,
  chiReading,
  madLabel,
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
  const { t } = useTranslation("app")
  const chi = chiReading(detail)

  return (
    <section className="flex flex-col gap-4">
      <SectionHead aside={`n = ${fmtCount(detail.n)}`}>
        {t("benford.firstDigitConformity")}
      </SectionHead>

      {detail.sufficient ? (
        <>
          <p className="max-w-2xl text-sm leading-relaxed text-pretty">
            {madReading(detail)}
            {chi && <span className="text-muted-foreground"> {chi}</span>}
          </p>

          <BenfordPlot data={detail.distribution} tall />

          <dl className="grid grid-cols-2 gap-x-6 gap-y-5 border-t pt-4 sm:grid-cols-3">
            <Reading label={t("matrix.mad")} emphasis>
              <span className={cn(detail.flagged && "text-destructive")}>
                {fmt(detail.mad)}
              </span>
            </Reading>
            <Reading label={t("benford.verdict")}>
              {madLabel(detail.mad_label) ?? detail.mad_label}
            </Reading>
            <Reading label={t("benford.nigriniLimit")}>
              {fmt(detail.threshold, 3)}
            </Reading>
            <Reading label={t("benford.bootstrap95")}>
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
            {t("benford.usableDropped", {
              usable: fmtCount(detail.n),
              dropped: detail.dropped,
            })}
          </p>
        </>
      ) : (
        <InsufficientSample detail={detail} />
      )}
    </section>
  )
}

function InsufficientSample({ detail }: { detail: BenfordDetail }) {
  const { t } = useTranslation("app")

  return (
    <div className="flex flex-col gap-2 border-l-2 border-destructive py-1 pl-4">
      <p className="text-sm font-medium text-destructive">
        {t("benford.notScored")}
      </p>
      <p className="max-w-2xl text-sm leading-relaxed text-pretty text-muted-foreground">
        {t("benford.insufficientBody", { total: fmtCount(detail.n) })}
      </p>
    </div>
  )
}
