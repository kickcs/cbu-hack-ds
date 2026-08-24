import { useState } from "react"
import { useTranslation } from "react-i18next"

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
  const { t } = useTranslation("ui")
  const [open, setOpen] = useState(false)
  const { clearing, clear } = useClearDocket()

  if (count === 0) return null

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button variant="ghost" size="sm" />}>
        {t("clearDocket.trigger")}
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {t("clearDocket.confirm", { count })}
          </DialogTitle>
        </DialogHeader>

        <DialogBody>
          <p className="text-muted-foreground">{t("clearDocket.body")}</p>
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            {t("clearDocket.keep")}
          </Button>
          <Button
            variant="destructive"
            disabled={clearing}
            onClick={() => {
              clear()
              setOpen(false)
            }}
          >
            {clearing ? t("clearDocket.clearing") : t("clearDocket.trigger")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
