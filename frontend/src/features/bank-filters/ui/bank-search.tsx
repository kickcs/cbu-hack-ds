import { SearchIcon } from "lucide-react"
import { useTranslation } from "react-i18next"

import { Input } from "@/shared/ui/input"

import { useBankFilters } from "../model/bank-filters-context"

export function BankSearch() {
  const { t } = useTranslation("ui")
  const { query, setQuery } = useBankFilters()

  return (
    <div className="relative">
      <SearchIcon className="pointer-events-none absolute top-1/2 left-2.5 size-3.5 -translate-y-1/2 text-muted-foreground" />
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={t("search.placeholder")}
        className="h-8 w-40 pl-8 text-xs sm:w-48"
        aria-label={t("search.placeholder")}
      />
    </div>
  )
}
