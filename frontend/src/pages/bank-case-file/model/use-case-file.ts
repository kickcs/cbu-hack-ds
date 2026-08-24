import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"

import {
  benfordQuery,
  evidenceQuery,
  latestAuditQuery,
  testCells,
  testColumns,
} from "@/entities/bank"

/**
 * A case file is one row of the latest audit plus its two detail calls. The row
 * comes from the ranked list, so the page also knows where the bank sits in it
 * and which banks are on either side.
 */
export function useCaseFile(bank: string) {
  const list = useQuery(latestAuditQuery())
  const benford = useQuery(benfordQuery(bank))
  const evidence = useQuery(evidenceQuery(bank))

  const rows = useMemo(() => list.data ?? [], [list.data])
  const index = rows.findIndex((row) => row.bank === bank)
  const audit = index === -1 ? null : rows[index]

  const cells = useMemo(
    () => (audit ? testCells(audit, testColumns(rows)) : []),
    [audit, rows]
  )

  return {
    audit,
    cells,
    rank: index + 1,
    total: rows.length,
    previous: index > 0 ? rows[index - 1] : null,
    next: index !== -1 && index < rows.length - 1 ? rows[index + 1] : null,
    detail: benford.data ?? null,
    evidence: evidence.data ?? null,
    /** The ranked list itself is still in flight, so the bank is unknown yet. */
    listLoading: list.isLoading,
    /** No such bank in the latest run — a stale link or a bank never audited. */
    missing: !list.isLoading && index === -1,
    detailLoading: benford.isLoading || evidence.isLoading,
    detailFailed: benford.isError || evidence.isError,
  }
}
