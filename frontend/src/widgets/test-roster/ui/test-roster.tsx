import { testLabel, type TestCell } from "@/entities/bank"
import { fmt } from "@/shared/lib/format"
import { cn } from "@/shared/lib/utils"
import { SectionHead } from "@/shared/ui/section-head"

/**
 * Every test the run applied to this bank, in matrix order, each with the thing
 * it looks for spelled out — the matrix squares are a summary, this is the read.
 */
export function TestRoster({ cells }: { cells: TestCell[] }) {
  const fired = cells.filter((cell) => cell.flagged).length

  return (
    <section className="flex flex-col gap-3">
      <SectionHead aside={`${fired} of ${cells.length} flagged`}>
        Test roster
      </SectionHead>
      <ul className="flex flex-col">
        {cells.map((cell) => (
          <RosterRow key={cell.test} cell={cell} />
        ))}
      </ul>
    </section>
  )
}

function RosterRow({ cell }: { cell: TestCell }) {
  const label = testLabel(cell.test)

  return (
    <li className="grid grid-cols-[3rem_1fr_auto] items-baseline gap-x-4 border-b border-border/60 py-3 last:border-b-0">
      <span
        className={cn(
          "code rounded-sm border px-1.5 py-0.5 text-center",
          cell.flagged
            ? "border-destructive bg-destructive text-background"
            : "border-border text-muted-foreground"
        )}
      >
        {label.code}
      </span>

      <div className="flex min-w-0 flex-col gap-1">
        <span className="text-sm font-medium">{label.name}</span>
        <span className="text-xs leading-relaxed text-pretty text-muted-foreground">
          {label.about}
        </span>
      </div>

      <div className="flex flex-col items-end gap-1 text-right">
        <span className="text-sm tabular-nums">
          {cell.score === null ? "—" : fmt(cell.score, 3)}
        </span>
        {cell.flagged ? (
          <a
            href={`#evidence-${cell.test}`}
            className="code text-destructive underline-offset-4 hover:underline focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
          >
            Flagged
          </a>
        ) : (
          <span className="code text-muted-foreground">Clear</span>
        )}
      </div>
    </li>
  )
}
