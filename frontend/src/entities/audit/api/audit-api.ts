import { apiClient } from "@/shared/api/client"

import type { Meta, RunResult } from "../model/types"

export const auditApi = {
  meta: async (signal?: AbortSignal) =>
    (await apiClient.get<Meta>("/api/meta", { signal })).data,
  run: async () => (await apiClient.post<RunResult>("/api/audit/run")).data,
}
