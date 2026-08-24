import { useTranslation } from "react-i18next"

import { cn } from "@/shared/lib/utils"

/** The mark an inspector puts on a file once the tests have run. */
export function VerdictStamp({
  flagged,
  className,
}: {
  flagged: boolean
  className?: string
}) {
  const { t } = useTranslation("ui")

  return (
    <span
      className={cn(
        "code inline-block -rotate-2 rounded-[3px] border-2 px-2 py-0.5 tracking-[0.16em]",
        flagged ? "border-destructive text-destructive" : "border-ok text-ok",
        className
      )}
    >
      {flagged ? t("verdictStamp.flagged") : t("verdictStamp.noFindings")}
    </span>
  )
}
