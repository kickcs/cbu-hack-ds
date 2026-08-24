import { useTranslation } from "react-i18next"

import {
  VerdictStamp,
  verdictLine,
  type BankAudit,
  type TestCell,
} from "@/entities/bank"
import { fmt, fmtCount } from "@/shared/lib/format"
import { cn } from "@/shared/lib/utils"
import { Reading } from "@/shared/ui/reading"

type Props = {
  audit: BankAudit
  rank: number
  total: number
  cells: TestCell[]
  /** Loan records behind the Benford reading, once the detail has loaded. */
  records: number | null
}

/** The cover of the case file: who it is about, and what the run concluded. */
export function CaseFileMasthead({
  audit,
  rank,
  total,
  cells,
  records,
}: Props) {
  const { t } = useTranslation("app")
  const fired = cells.filter((cell) => cell.flagged).length

  return (
    <section
      className={cn(
        "flex flex-col gap-4 border-l-2 pl-5",
        audit.suspicious ? "border-destructive" : "border-ok"
      )}
    >
      <p className="eyebrow">
        {t("caseFile.rank", { rank, total })}
      </p>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-3">
        <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
          {audit.bank}
        </h1>
        <VerdictStamp flagged={audit.suspicious} />
      </div>

      <p className="max-w-2xl text-base leading-relaxed text-pretty">
        {verdictLine(cells)}
      </p>

      <dl className="grid grid-cols-2 gap-x-6 gap-y-5 border-t pt-4 sm:grid-cols-4 sm:gap-x-10">
        <Reading label={t("caseFile.findings")} emphasis>
          <span className={cn(fired > 0 && "text-destructive")}>
            {t("caseFile.firedOf", { fired, total: cells.length })}
          </span>
        </Reading>
        <Reading label={t("caseFile.compositeScore")} emphasis>
          {fmt(audit.composite, 2)}
        </Reading>
        <Reading label={t("matrix.mad")} emphasis>
          {/* Withheld below 300 loans, so the figure is not shown as if it were one. */}
          <span className={cn(audit.benford.flagged && "text-destructive")}>
            {audit.benford.sufficient ? fmt(audit.benford.mad) : "—"}
          </span>
        </Reading>
        <Reading label={t("caseFile.loanRecords")} emphasis>
          {records === null ? "—" : fmtCount(records)}
        </Reading>
      </dl>
    </section>
  )
}
