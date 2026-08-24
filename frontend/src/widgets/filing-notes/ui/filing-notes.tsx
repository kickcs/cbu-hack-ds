import { useTranslation } from "react-i18next"

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
  const { t } = useTranslation("app")

  if (issues.length === 0 && skipped.length === 0) return null

  const errors = issues.filter((issue) => issue.level === "error")
  const warnings = issues.filter((issue) => issue.level === "warning")

  return (
    <section className="flex flex-col gap-3">
      <SectionHead
        aside={
          skipped.length > 0
            ? `${t("filingNotes.onData", { count: issues.length })} · ${t("filingNotes.testsSkipped", { count: skipped.length })}`
            : t("filingNotes.onData", { count: issues.length })
        }
      >
        {t("filingNotes.remarks")}
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
  const { t } = useTranslation("app")
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
        {bad ? t("filingNotes.error") : t("filingNotes.warning")}
        {issue.file && ` · ${issue.file}`}
      </p>
    </li>
  )
}

function Skipped({ tests }: { tests: string[] }) {
  const { t } = useTranslation("app")
  const names = tests.map((test) => testLabel(test).name.toLowerCase()).join(", ")
  const codes = tests.map((test) => testLabel(test).code).join(" · ")

  return (
    <li className="border-l-2 py-0.5 pl-4">
      <p className="text-sm leading-relaxed text-pretty">
        {t("filingNotes.skippedLine", { count: tests.length, names })}{" "}
        {t("filingNotes.skippedCoda")}
      </p>
      <p className="code mt-1 text-muted-foreground">
        {t("filingNotes.skippedPrefix", { codes })}
      </p>
    </li>
  )
}
