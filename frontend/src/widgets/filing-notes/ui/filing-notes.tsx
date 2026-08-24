import { testLabel } from "@/entities/bank"
import type { Issue } from "@/entities/submission"
import { cn } from "@/shared/lib/utils"
import { SectionHead } from "@/shared/ui/section-head"

type Props = {
  issues: Issue[]
  /** Tests with no input in this filing. Not run is not the same as passed. */
  skipped: string[]
}

/**
 * The clerk's remarks in the margin of the filing: what was wrong with the data
 * and which tests it could not answer. Nothing here was repaired silently — a
 * defect is reported and the rows it touched are left out of the reading.
 */
export function FilingNotes({ issues, skipped }: Props) {
  if (issues.length === 0 && skipped.length === 0) return null

  const errors = issues.filter((issue) => issue.level === "error")
  const warnings = issues.filter((issue) => issue.level === "warning")

  return (
    <section className="flex flex-col gap-3">
      <SectionHead
        aside={
          skipped.length > 0
            ? `${issues.length} on the data · ${skipped.length} tests skipped`
            : `${issues.length} on the data`
        }
      >
        Remarks
      </SectionHead>

      <ul className="flex flex-col gap-2.5">
        {[...errors, ...warnings].map((issue, i) => (
          <Remark key={`${issue.code}-${i}`} issue={issue} />
        ))}

        {skipped.length > 0 && <Skipped tests={skipped} />}
      </ul>
    </section>
  )
}

function Remark({ issue }: { issue: Issue }) {
  const bad = issue.level === "error"

  return (
    <li
      className={cn(
        "border-l-2 py-0.5 pl-4",
        bad ? "border-destructive" : "border-border"
      )}
    >
      <p className="text-sm leading-relaxed text-pretty">{issue.message}</p>
      {/* The tally is already in the sentence, so the line under it just files the remark. */}
      <p className="code mt-1 text-muted-foreground">
        {bad ? "Error" : "Warning"}
        {issue.file && ` · ${issue.file}`}
      </p>
    </li>
  )
}

function Skipped({ tests }: { tests: string[] }) {
  return (
    <li className="border-l-2 py-0.5 pl-4">
      <p className="text-sm leading-relaxed text-pretty">
        {tests.length === 1 ? "One test was" : `${tests.length} tests were`} not
        run: this filing carried no input for{" "}
        {tests.map((test) => testLabel(test).name.toLowerCase()).join(", ")}. A
        test that did not run is not a test that passed.
      </p>
      <p className="code mt-1 text-muted-foreground">
        Skipped · {tests.map((test) => testLabel(test).code).join(" · ")}
      </p>
    </li>
  )
}
