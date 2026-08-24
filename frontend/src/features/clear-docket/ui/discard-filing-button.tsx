import { useEffect, useState } from "react"
import { Trash2Icon } from "lucide-react"

import { docketNo } from "@/entities/submission"
import { Button } from "@/shared/ui/button"

import { useDiscardFiling } from "../model/use-clear-docket"

/**
 * Discarding one filing is two presses, not a dialog: the row is small enough
 * to ask in place, and the armed state gives it back if the press was a slip.
 */
export function DiscardFilingButton({ id }: { id: number }) {
  const [armed, setArmed] = useState(false)
  const { discarding, discard } = useDiscardFiling()

  // The question expires on its own, so no row is left sitting armed.
  useEffect(() => {
    if (!armed) return
    const timer = setTimeout(() => setArmed(false), 4_000)
    return () => clearTimeout(timer)
  }, [armed])

  if (armed) {
    return (
      <span className="flex items-center gap-1">
        <Button
          variant="destructive"
          size="xs"
          disabled={discarding}
          onClick={() => discard(id)}
        >
          Discard
        </Button>
        <Button variant="ghost" size="xs" onClick={() => setArmed(false)}>
          Keep
        </Button>
      </span>
    )
  }

  return (
    <Button
      variant="ghost"
      size="icon-sm"
      onClick={() => setArmed(true)}
      className="text-muted-foreground hover:text-destructive"
    >
      <Trash2Icon />
      <span className="sr-only">Discard filing {docketNo(id)}</span>
    </Button>
  )
}
