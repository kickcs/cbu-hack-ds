import { useState } from "react"

import {
  BenfordPlot,
  ExceptionCell,
  MAD_LABELS,
  evidenceColumnHead,
  fmtEvidenceCell,
  testCells,
  testColumns,
  testLabel,
  VerdictStamp,
  type BankAudit,
  type BenfordDetail,
  type Evidence,
  type EvidenceBlock,
} from "@/entities/bank"
import { fmt, fmtCount } from "@/shared/lib/format"
import { cn } from "@/shared/lib/utils"
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog"
import { Skeleton } from "@/shared/ui/skeleton"

import { useBankDossier } from "../model/use-bank-dossier"

/** The case file behind one row of the matrix: the chart, the readings, the proof. */
export function BankDossier({
  audit,
  onClose,
}: {
  audit: BankAudit | null
  onClose: () => void
}) {
  // `audit` clears the moment the dialog starts closing, so hold the last bank
  // until the animation finishes — otherwise the contents collapse on screen.
  const [retained, setRetained] = useState(audit)
  if (audit !== null && audit.bank !== retained?.bank) setRetained(audit)
  const shown = audit ?? retained

  const { detail, evidence, loading, failed } = useBankDossier(
    shown?.bank ?? null
  )

  return (
    <Dialog open={audit !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-3xl">
        {shown && (
          <>
            <Header audit={shown} />
            <DialogBody className="flex flex-col gap-5">
              {failed && !loading && (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  Couldn't load the detail for this bank. Re-run the audit and
                  try again.
                </p>
              )}
              {loading && <LoadingBody />}
              {detail && !loading && (
                <>
                  <BenfordSection detail={detail} />
                  <TestResults audit={shown} />
                  <EvidenceSection evidence={evidence} />
                </>
              )}
            </DialogBody>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}

function Header({ audit }: { audit: BankAudit }) {
  const fired = testCells(audit, testColumns([audit])).filter((c) => c.flagged)

  return (
    <DialogHeader className="pr-10">
      <DialogTitle className="flex flex-wrap items-center gap-3 font-display text-lg tracking-tight">
        {audit.bank}
        <VerdictStamp flagged={audit.suspicious} />
      </DialogTitle>
      <DialogDescription>
        {fired.length
          ? `Failed: ${fired.map((c) => testLabel(c.test).name).join(", ")}`
          : "No test returned a finding for this bank."}
      </DialogDescription>
    </DialogHeader>
  )
}

function LoadingBody() {
  return (
    <div className="flex flex-col gap-5">
      <Skeleton className="h-56 w-full" />
      <Skeleton className="h-28 w-full" />
    </div>
  )
}

function SectionHead({ children }: { children: React.ReactNode }) {
  return <h3 className="eyebrow border-b pb-1.5">{children}</h3>
}

function BenfordSection({ detail }: { detail: BenfordDetail }) {
  const verdict = MAD_LABELS[detail.mad_label] ?? detail.mad_label

  return (
    <section className="flex flex-col gap-3">
      <SectionHead>First-digit conformity</SectionHead>

      {detail.sufficient ? (
        <BenfordPlot data={detail.distribution} />
      ) : (
        <p className="rounded-md border border-destructive/40 bg-destructive/5 px-3 py-2.5 text-xs text-muted-foreground">
          <span className="font-medium text-destructive">
            Not scored on Benford.
          </span>{" "}
          This bank filed {fmtCount(detail.n)} usable loan amounts, below the
          minimum sample the test needs to separate a real deviation from noise.
        </p>
      )}

      <dl className="flex flex-wrap items-baseline gap-x-6 gap-y-2 border-t pt-3">
        <Reading label="MAD" wide>
          <span className={cn(detail.flagged && "text-destructive")}>
            {fmt(detail.mad)}
          </span>
        </Reading>
        <Reading label="Verdict" wide>
          {verdict}
        </Reading>
        <Reading label="χ²" keepCase>
          {fmt(detail.chi2, 1)}
        </Reading>
        <Reading label="p" keepCase>
          {fmt(detail.chi2_p, 4)}
        </Reading>
      </dl>

      <p className="text-[0.7rem] tracking-wide text-muted-foreground tabular-nums">
        n = {fmtCount(detail.n)} · {detail.dropped} dropped · Nigrini limit{" "}
        {fmt(detail.threshold, 3)} · bootstrap 95th pct{" "}
        {fmt(detail.calibrated_threshold, 4)}
      </p>
    </section>
  )
}

function Reading({
  label,
  wide,
  keepCase,
  children,
}: {
  label: string
  wide?: boolean
  /** For symbols like χ² and p, where uppercasing would change the notation. */
  keepCase?: boolean
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className={cn("eyebrow", keepCase && "normal-case")}>{label}</dt>
      <dd
        className={cn(
          "tabular-nums",
          wide ? "text-base font-medium" : "text-sm"
        )}
      >
        {children}
      </dd>
    </div>
  )
}

function TestResults({ audit }: { audit: BankAudit }) {
  const cells = testCells(audit, testColumns([audit]))

  return (
    <section className="flex flex-col gap-3">
      <SectionHead>Test results</SectionHead>
      <ul className="grid grid-cols-1 gap-x-6 sm:grid-cols-2">
        {cells.map((cell) => {
          const label = testLabel(cell.test)
          return (
            <li
              key={cell.test}
              className="flex items-center gap-2.5 border-b border-border/60 py-1.5 last:border-b-0 sm:last:border-b"
              title={label.about}
            >
              <ExceptionCell cell={cell} />
              <span className={cn("flex-1", !cell.flagged && "text-muted-foreground")}>
                {label.name}
              </span>
              <span
                className={cn(
                  "text-xs tabular-nums",
                  cell.flagged ? "text-destructive" : "text-muted-foreground"
                )}
              >
                {cell.score === null ? "—" : fmt(cell.score, 3)}
              </span>
            </li>
          )
        })}
      </ul>
    </section>
  )
}

function EvidenceSection({ evidence }: { evidence: Evidence | null }) {
  if (!evidence || evidence.blocks.length === 0) return null

  return (
    <section className="flex flex-col gap-3">
      <SectionHead>Evidence</SectionHead>
      {evidence.blocks.map((block) => (
        <EvidenceTable key={block.test} block={block} />
      ))}
    </section>
  )
}

function EvidenceTable({ block }: { block: EvidenceBlock }) {
  const columns = block.rows.length
    ? Object.keys(block.rows[0]).filter((k) => k !== "suspect")
    : []

  return (
    <article className="flex min-w-0 flex-col gap-1.5 rounded-md border border-destructive/30 bg-destructive/5 p-3">
      <h4 className="text-xs font-semibold">{block.title}</h4>
      <p className="text-[0.7rem] text-muted-foreground">{block.summary}</p>
      <div className="mt-1 overflow-x-auto">
        <table className="ledger w-full text-left text-[0.7rem]">
          <thead>
            <tr className="border-b border-border/60">
              {columns.map((column) => (
                <th
                  key={column}
                  scope="col"
                  className="py-1 pr-3 text-[0.625rem] font-medium tracking-wider text-muted-foreground uppercase"
                >
                  {evidenceColumnHead(column)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {block.rows.map((row, i) => (
              <tr
                key={i}
                className={cn(
                  "border-b border-border/40 last:border-b-0",
                  row.suspect && "font-medium text-destructive"
                )}
              >
                {columns.map((column) => (
                  <td
                    key={column}
                    className="py-1 pr-3 whitespace-nowrap tabular-nums"
                  >
                    {fmtEvidenceCell(column, row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </article>
  )
}
