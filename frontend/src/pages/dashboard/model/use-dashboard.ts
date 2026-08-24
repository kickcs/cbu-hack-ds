import { useQuery } from "@tanstack/react-query"

import { metaQuery } from "@/entities/audit"
import { latestAuditQuery } from "@/entities/bank"

export function useDashboard() {
  const meta = useQuery(metaQuery())
  const rows = useQuery(latestAuditQuery())

  return {
    meta: meta.data ?? null,
    rows: rows.data ?? null,
    loading: meta.isLoading || rows.isLoading,
  }
}
