import { queryOptions, skipToken } from "@tanstack/react-query"

import { bankApi } from "./bank-api"

export const bankKeys = {
  all: ["bank"] as const,
  latest: () => [...bankKeys.all, "latest"] as const,
  benford: (bank: string | null) => [...bankKeys.all, "benford", bank] as const,
  evidence: (bank: string | null) =>
    [...bankKeys.all, "evidence", bank] as const,
}

export const latestAuditQuery = () =>
  queryOptions({
    queryKey: bankKeys.latest(),
    queryFn: ({ signal }) => bankApi.latest(signal),
  })

export const benfordQuery = (bank: string | null) =>
  queryOptions({
    queryKey: bankKeys.benford(bank),
    queryFn:
      bank === null ? skipToken : ({ signal }) => bankApi.benford(bank, signal),
  })

export const evidenceQuery = (bank: string | null) =>
  queryOptions({
    queryKey: bankKeys.evidence(bank),
    queryFn:
      bank === null
        ? skipToken
        : ({ signal }) => bankApi.evidence(bank, signal),
  })
