import { useTranslation } from "react-i18next"

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
  const { t } = useTranslation("app")

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
    t("lede.loanRecords", { count: meta.register_rows, total: fmtCount(meta.register_rows) }),
    t("lede.filedLines", { count: meta.report_rows, total: fmtCount(meta.report_rows) }),
    t("lede.prudentialReadings", { count: meta.normativ_rows, total: fmtCount(meta.normativ_rows) }),
    t("lede.tests", { count: testCount, total: testCount }),
  ].join("  ·  ")

  return (
    <div className="flex flex-col gap-3 py-2">
      <p className="eyebrow">{t("lede.statisticalExceptionReport")}</p>

      <h1 className="max-w-3xl font-display text-2xl leading-snug font-semibold tracking-tight text-balance sm:text-3xl">
        {flagged > 0 ? (
          t("lede.failed", { flagged, total })
        ) : (
          t("lede.passed", { banks: t("lede.banks", { count: total }) })
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
  const { t } = useTranslation("app")

  if (insufficient.length === 0) {
    return (
      <p className="border-l-2 border-ok py-0.5 pl-3 text-xs text-muted-foreground">
        {t("lede.sampleOk", { minSample })}
      </p>
    )
  }

  return (
    <p className="border-l-2 border-destructive py-0.5 pl-3 text-xs">
      <span className="font-medium text-destructive">
        {t("lede.sampleTooSmall")}
      </span>{" "}
      <span className="text-muted-foreground">
        {t("lede.sampleSmallBody", {
          banks: insufficient.join(", "),
          minSample,
        })}
      </span>
    </p>
  )
}
