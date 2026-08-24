import { RefreshCwIcon } from "lucide-react"
import { useTranslation } from "react-i18next"

import { cn } from "@/shared/lib/utils"
import { Button } from "@/shared/ui/button"

import { useRunAudit } from "../model/use-run-audit"

export function RunAuditButton() {
  const { t } = useTranslation("ui")
  const { running, run } = useRunAudit()

  return (
    <Button onClick={() => run()} disabled={running} size="sm">
      <RefreshCwIcon
        data-icon="inline-start"
        className={cn(running && "animate-spin")}
      />
      {running ? t("runAudit.running") : t("runAudit.run")}
    </Button>
  )
}
