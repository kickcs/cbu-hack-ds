import { useTranslation } from "react-i18next"

import { Button } from "@/shared/ui/button"

import { useBankFilters } from "../model/bank-filters-context"

export function FlaggedToggle() {
  const { t } = useTranslation("ui")
  const { flaggedOnly, toggleFlaggedOnly } = useBankFilters()

  return (
    <Button
      variant={flaggedOnly ? "default" : "outline"}
      size="sm"
      aria-pressed={flaggedOnly}
      onClick={toggleFlaggedOnly}
      className="h-8 text-xs"
    >
      {t("flagged.label")}
    </Button>
  )
}
