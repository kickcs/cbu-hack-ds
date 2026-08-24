import { queryOptions } from "@tanstack/react-query"

import { auditApi } from "./audit-api"

export const auditKeys = {
  all: ["audit"] as const,
  meta: () => [...auditKeys.all, "meta"] as const,
}

export const metaQuery = () =>
  queryOptions({
    queryKey: auditKeys.meta(),
    queryFn: ({ signal }) => auditApi.meta(signal),
  })
