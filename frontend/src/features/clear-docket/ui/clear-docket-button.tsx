import { useState } from "react"

import { Button } from "@/shared/ui/button"
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/shared/ui/dialog"

import { useClearDocket } from "../model/use-clear-docket"

/** Emptying the docket destroys every filing and its stored files at once. */
export function ClearDocketButton({ count }: { count: number }) {
  const [open, setOpen] = useState(false)
  const { clearing, clear } = useClearDocket()

  if (count === 0) return null

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button variant="ghost" size="sm" />}>
        Clear the docket
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Clear the docket of {count === 1 ? "1 filing" : `${count} filings`}?
          </DialogTitle>
        </DialogHeader>

        <DialogBody>
          <p className="text-muted-foreground">
            Every filing and the files uploaded with it are deleted. The
            supervisory dataset and the matrix on the front page are untouched.
          </p>
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Keep them
          </Button>
          <Button
            variant="destructive"
            disabled={clearing}
            onClick={() => {
              clear()
              setOpen(false)
            }}
          >
            {clearing ? "Clearing…" : "Clear the docket"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
