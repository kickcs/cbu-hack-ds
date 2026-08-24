import { apiClient } from "@/shared/api/client"

import type { BankAudit, BenfordDetail, Evidence } from "../model/types"

export const bankApi = {
  latest: async (signal?: AbortSignal) =>
    (await apiClient.get<BankAudit[]>("/api/audit/latest", { signal })).data,

  benford: async (bank: string, signal?: AbortSignal) =>
    (
      await apiClient.get<BenfordDetail>(
        `/api/banks/${encodeURIComponent(bank)}/benford`,
        { signal }
      )
    ).data,

  evidence: async (bank: string, signal?: AbortSignal) =>
    (
      await apiClient.get<Evidence>(
        `/api/banks/${encodeURIComponent(bank)}/evidence`,
        { signal }
      )
    ).data,
}
