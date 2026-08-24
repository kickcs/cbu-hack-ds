import { useTranslation } from "react-i18next"

import {
  evidenceColumnHead,
  evidenceSummary,
  evidenceTitle,
  fmtEvidenceCell,
  testLabel,
  type Evidence,
  type EvidenceBlock,
} from "@/entities/bank"
import { cn } from "@/shared/lib/utils"
import { SectionHead } from "@/shared/ui/section-head"

/** The figures behind each finding, one exhibit per test that fired. */
export function EvidenceLog({ evidence }: { evidence: Evidence }) {
  const { t } = useTranslation("app")

  if (evidence.blocks.length === 0) return null

  return (
    <section className="flex flex-col gap-4">
      <SectionHead
        aside={t("evidence.exhibits", {
          count: evidence.blocks.length,
          total: evidence.blocks.length,
        })}
      >
        {t("evidence.title")}
      </SectionHead>
      {evidence.blocks.map((block) => (
        <Exhibit key={block.test} block={block} />
      ))}
    </section>
  )
}

function Exhibit({ block }: { block: EvidenceBlock }) {
  const { t } = useTranslation("app")
  const columns = block.rows.length
    ? Object.keys(block.rows[0]).filter((key) => key !== "suspect")
    : []
  const suspects = block.rows.filter((row) => row.suspect).length

  return (
    <article
      id={`evidence-${block.test}`}
      className="flex min-w-0 scroll-mt-24 flex-col gap-3 rounded-md border border-l-2 border-l-destructive bg-card p-4"
    >
      <header className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="code rounded-sm border border-destructive px-1.5 py-0.5 text-destructive">
          {testLabel(block.test).code}
        </span>
        <h3 className="font-display text-sm font-semibold tracking-tight">
          {evidenceTitle(block)}
        </h3>
      </header>

      <p className="max-w-2xl text-sm leading-relaxed text-pretty text-muted-foreground">
        {evidenceSummary(block)}
      </p>

      <div className="-mx-1 overflow-x-auto px-1">
        <table className="ledger w-full text-left text-[0.8125rem]">
          <caption className="sr-only">
            {t("evidence.caption", {
              title: evidenceTitle(block),
              suspects,
              total: block.rows.length,
            })}
          </caption>
          <thead>
            <tr className="border-b">
              <th scope="col" className="w-6">
                <span className="sr-only">{t("evidence.suspect")}</span>
              </th>
              {columns.map((column) => (
                <th
                  key={column}
                  scope="col"
                  className="py-1.5 pr-4 text-[0.625rem] font-medium tracking-[0.12em] text-muted-foreground uppercase"
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
                <td className="py-2">
                  {row.suspect && (
                    <span
                      role="img"
                      aria-label={t("evidence.suspect")}
                      className="block size-2 rounded-[1px] bg-destructive"
                    />
                  )}
                </td>
                {columns.map((column) => (
                  <td
                    key={column}
                    className="py-2 pr-4 whitespace-nowrap tabular-nums"
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
