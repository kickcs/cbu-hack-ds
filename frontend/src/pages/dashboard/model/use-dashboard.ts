import { useQuery } from "@tanstack/react-query"
import { useState } from "react"

import { metaQuery } from "@/entities/audit"
import { latestAuditQuery, type BankAudit } from "@/entities/bank"

export function useDashboard() {
  const meta = useQuery(metaQuery())
  const rows = useQuery(latestAuditQuery())
  const [selected, setSelected] = useState<BankAudit | null>(null)

  return {
    meta: meta.data ?? null,
    rows: rows.data ?? null,
    loading: meta.isLoading || rows.isLoading,
    selected,
    select: setSelected,
    closeSelected: () => setSelected(null),
  }
}
