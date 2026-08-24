import { testLabel } from "@/entities/bank"
import { cn } from "@/shared/lib/utils"

import { useBankFilters } from "../model/bank-filters-context"

/**
 * Doubles as the key to the matrix and the way to narrow it: each entry names a
 * column and, when pressed, keeps only the banks that column flagged.
 */
export function TestLegend({ tests }: { tests: string[] }) {
  const { tests: selected, toggleTest } = useBankFilters()

  return (
    <div className="flex flex-wrap items-center gap-x-1 gap-y-1">
      {tests.map((test) => {
        const label = testLabel(test)
        const on = selected.includes(test)
        return (
          <button
            key={test}
            type="button"
            aria-pressed={on}
            title={label.about}
            onClick={() => toggleTest(test)}
            className={cn(
              "flex items-center gap-1.5 rounded-sm border px-1.5 py-1 text-[0.7rem] transition-colors",
              "focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none",
              on
                ? "border-foreground/40 bg-accent text-foreground"
                : "border-transparent text-muted-foreground hover:bg-accent/60 hover:text-foreground"
            )}
          >
            <span className="code">{label.code}</span>
            <span>{label.name}</span>
          </button>
        )
      })}
    </div>
  )
}
