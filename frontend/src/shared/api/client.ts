import axios from "axios"

import i18n from "@/shared/lib/i18n"

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  timeout: 30_000,
})

export function apiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) return i18n.t("common:errors.generic")

  if (error.code === "ERR_NETWORK" || error.code === "ECONNABORTED") {
    return i18n.t("common:errors.network")
  }

  const detail = (error.response?.data as { detail?: unknown } | undefined)
    ?.detail
  if (typeof detail === "string") return detail

  return i18n.t("common:errors.http", {
    status: error.response?.status ?? "?",
    statusText: error.response?.statusText ?? "",
  })
}
