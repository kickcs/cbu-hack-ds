import { queryOptions, skipToken } from "@tanstack/react-query"

import { isOpen } from "../model/types"
import { submissionApi } from "./submission-api"

export const submissionKeys = {
  all: ["submission"] as const,
  list: () => [...submissionKeys.all, "list"] as const,
  one: (id: number | null) => [...submissionKeys.all, "one", id] as const,
}

/** How often to ask again while a filing is still in hand. */
const POLL_MS = 1_500

export const filingsQuery = () =>
  queryOptions({
    queryKey: submissionKeys.list(),
    queryFn: ({ signal }) => submissionApi.list(signal),
    // Polling stops as soon as the docket has nothing open, so an idle
    // dashboard makes no requests at all.
    refetchInterval: ({ state }) =>
      state.data?.some(isOpen) ? POLL_MS : false,
  })

export const filingQuery = (id: number | null) =>
  queryOptions({
    queryKey: submissionKeys.one(id),
    queryFn:
      id === null ? skipToken : ({ signal }) => submissionApi.get(id, signal),
    refetchInterval: ({ state }) =>
      state.data && isOpen(state.data) ? POLL_MS : false,
  })
