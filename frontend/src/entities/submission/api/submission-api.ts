import { apiClient } from "@/shared/api/client"

import type { Filing, FilingReport } from "../model/types"

export const submissionApi = {
  list: async (signal?: AbortSignal) =>
    (await apiClient.get<Filing[]>("/api/submissions", { signal })).data,

  get: async (id: number, signal?: AbortSignal) =>
    (await apiClient.get<FilingReport>(`/api/submissions/${id}`, { signal }))
      .data,

  /** Uploading is one request per filing: every file goes in the same form. */
  upload: async (files: File[]) => {
    const form = new FormData()
    files.forEach((file) => form.append("files", file))
    return (
      await apiClient.post<Filing>("/api/submissions", form, {
        // Large registers take a while to reach the queue; the audit itself is not waited on.
        timeout: 120_000,
      })
    ).data
  },

  remove: async (id: number) => {
    await apiClient.delete(`/api/submissions/${id}`)
  },

  clear: async () =>
    (await apiClient.delete<{ deleted: number }>("/api/submissions")).data,
}
