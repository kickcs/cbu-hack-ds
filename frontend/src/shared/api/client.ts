import axios from "axios"

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  timeout: 30_000,
})

export function apiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) return "Something went wrong"

  if (error.code === "ERR_NETWORK" || error.code === "ECONNABORTED") {
    return "The API is not answering — check that it is running on :8000"
  }

  const detail = (error.response?.data as { detail?: unknown } | undefined)
    ?.detail
  if (typeof detail === "string") return detail

  return `HTTP ${error.response?.status ?? "?"} ${error.response?.statusText ?? ""}`.trim()
}
