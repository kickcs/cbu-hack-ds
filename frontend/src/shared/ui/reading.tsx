import type { ReactNode } from "react"

import { cn } from "@/shared/lib/utils"

/** A single labelled figure, as a report prints it: caption over value. */
export function Reading({
  label,
  keepCase,
  emphasis,
  children,
}: {
  label: string
  /** For symbols like χ² and p, where uppercasing would change the notation. */
  keepCase?: boolean
  emphasis?: boolean
  children: ReactNode
}) {
  return (
    <div className="flex flex-col gap-1">
      <dt className={cn("eyebrow", keepCase && "normal-case")}>{label}</dt>
      <dd
        className={cn(
          "tabular-nums",
          emphasis ? "text-lg leading-none font-semibold" : "text-sm"
        )}
      >
        {children}
      </dd>
    </div>
  )
}
