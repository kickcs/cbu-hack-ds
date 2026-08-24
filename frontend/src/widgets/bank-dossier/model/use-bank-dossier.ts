import { useQuery } from "@tanstack/react-query"

import { benfordQuery, evidenceQuery } from "@/entities/bank"

export function useBankDossier(bank: string | null) {
  const detail = useQuery(benfordQuery(bank))
  const evidence = useQuery(evidenceQuery(bank))

  return {
    detail: detail.data ?? null,
    evidence: evidence.data ?? null,
    loading: detail.isLoading || evidence.isLoading,
    failed: detail.isError || evidence.isError,
  }
}
