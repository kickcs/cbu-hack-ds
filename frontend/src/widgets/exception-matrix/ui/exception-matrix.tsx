import { useMemo } from "react"

import {
  ExceptionCell,
  testCells,
  testColumns,
  testLabel,
  type BankAudit,
} from "@/entities/bank"
import {
  BankFiltersProvider,
  BankSearch,
  FlaggedToggle,
  TestLegend,
  useBankFilters,
} from "@/features/bank-filters"
import { fmt } from "@/shared/lib/format"
import { cn } from "@/shared/lib/utils"
import { Button } from "@/shared/ui/button"
import { Skeleton } from "@/shared/ui/skeleton"

type Props = {
  rows: BankAudit[]
  loading: boolean
  onSelect: (audit: BankAudit) => void
}

/**
 * One row per bank, one column per test: the whole supervisory picture in a
 * single read. Solid cells are findings, tinted cells are near misses.
 */
export function ExceptionMatrix({ rows, loading, onSelect }: Props) {
  const tests = useMemo(() => testColumns(rows), [rows])

  return (
    <BankFiltersProvider>
      <section className="overflow-hidden rounded-lg border bg-card">
        <Toolbar />
        {loading ? <LoadingRows /> : <Matrix rows={rows} tests={tests} onSelect={onSelect} />}
        <footer className="border-t px-4 py-3">
          <p className="eyebrow mb-2">Tests — press to narrow the matrix</p>
          <TestLegend tests={tests} />
        </footer>
      </section>
    </BankFiltersProvider>
  )
}

function Toolbar() {
  return (
    <header className="flex flex-wrap items-end justify-between gap-3 border-b px-4 py-3">
      <div>
        <h2 className="font-display text-sm font-semibold tracking-tight">
          Exception matrix
        </h2>
        <p className="mt-0.5 text-xs text-muted-foreground">
          Ranked by composite score, worst first
        </p>
      </div>
      <div className="flex items-center gap-2">
        <BankSearch />
        <FlaggedToggle />
      </div>
    </header>
  )
}

function LoadingRows() {
  return (
    <div className="flex flex-col gap-2 px-4 py-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <Skeleton key={i} className="h-7 w-full" />
      ))}
    </div>
  )
}

function Matrix({
  rows,
  tests,
  onSelect,
}: Omit<Props, "loading"> & { tests: string[] }) {
  const { filter, active, clear } = useBankFilters()

  const visible = useMemo(() => filter(rows), [filter, rows])

  if (visible.length === 0) {
    return (
      <div className="flex flex-col items-center gap-3 px-4 py-14 text-center">
        <p className="text-sm text-muted-foreground">
          No bank matches the current filters.
        </p>
        {active && (
          <Button variant="outline" size="sm" onClick={clear}>
            Clear filters
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="ledger w-full border-collapse text-xs">
        <thead>
          <tr>
            <th className="w-9" />
            <th className="w-full" />
            <th
              colSpan={tests.length}
              className="eyebrow hidden border-x border-b px-2 pt-2 pb-1 text-center font-normal md:table-cell"
            >
              Tests
            </th>
            <th colSpan={3} />
          </tr>
          <tr className="border-b">
            <Head className="w-9 text-right">#</Head>
            <Head className="text-left">Bank</Head>
            {tests.map((test, i) => {
              const label = testLabel(test)
              return (
                <Head
                  key={test}
                  title={`${label.name} — ${label.about}`}
                  className={cn(
                    "hidden w-8 text-center md:table-cell",
                    i === 0 && "border-l",
                    i === tests.length - 1 && "border-r"
                  )}
                >
                  {label.code}
                </Head>
              )
            })}
            <Head className="w-20 text-right">MAD</Head>
            <Head className="hidden w-14 text-right normal-case sm:table-cell">
              n
            </Head>
            <Head className="w-16 text-right">Score</Head>
          </tr>
        </thead>

        <tbody>
          {visible.map((row, i) => (
            <Row
              key={row.bank}
              row={row}
              rank={i + 1}
              tests={tests}
              onSelect={onSelect}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Head({
  className,
  children,
  title,
}: {
  className?: string
  children?: React.ReactNode
  title?: string
}) {
  return (
    <th
      scope="col"
      title={title}
      className={cn(
        "px-2 pb-1.5 text-[0.625rem] font-medium tracking-[0.12em] text-muted-foreground uppercase",
        className
      )}
    >
      {children}
    </th>
  )
}

function Row({
  row,
  rank,
  tests,
  onSelect,
}: {
  row: BankAudit
  rank: number
  tests: string[]
  onSelect: (audit: BankAudit) => void
}) {
  const cells = testCells(row, tests)
  const fired = cells.filter((c) => c.flagged)

  return (
    <tr
      onClick={() => onSelect(row)}
      style={{ animationDelay: `${Math.min(rank, 14) * 22}ms` }}
      className="row-in cursor-pointer border-b border-border/60 transition-colors last:border-b-0 hover:bg-accent"
    >
      <td
        className={cn(
          "border-l-2 py-1.5 pr-2 pl-2 text-right text-muted-foreground tabular-nums",
          row.suspicious ? "border-l-destructive" : "border-l-transparent"
        )}
      >
        {rank}
      </td>

      <td className="py-1.5 pr-3">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation()
            onSelect(row)
          }}
          className="rounded-sm text-left font-medium hover:underline focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
        >
          {row.bank}
        </button>
        {fired.length > 0 && (
          <span className="mt-1 flex flex-wrap gap-1 md:hidden">
            {fired.map((cell) => (
              <span
                key={cell.test}
                className="code rounded-sm bg-destructive/12 px-1 py-px text-[0.5625rem] text-destructive"
              >
                {testLabel(cell.test).code}
              </span>
            ))}
          </span>
        )}
      </td>

      {cells.map((cell, i) => (
        <td
          key={cell.test}
          className={cn(
            "hidden px-2 py-1.5 md:table-cell",
            i === 0 && "border-l",
            i === cells.length - 1 && "border-r"
          )}
        >
          <span className="flex justify-center">
            <ExceptionCell cell={cell} delay={rank * 22 + i * 35} />
          </span>
        </td>
      ))}

      <td
        className={cn(
          "px-2 py-1.5 text-right tabular-nums",
          row.benford.flagged && "font-medium text-destructive"
        )}
      >
        {fmt(row.benford.mad)}
      </td>

      <td className="hidden px-2 py-1.5 text-right text-muted-foreground tabular-nums sm:table-cell">
        {row.benford.sufficient ? row.benford.n : "—"}
      </td>

      <td
        className={cn(
          "px-2 py-1.5 text-right tabular-nums",
          row.suspicious ? "font-medium" : "text-muted-foreground"
        )}
      >
        {fmt(row.composite, 2)}
      </td>
    </tr>
  )
}
