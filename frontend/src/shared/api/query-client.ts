import { QueryCache, QueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { apiErrorMessage } from "./client"

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    // общий id: параллельные запросы падают вместе, тост нужен один
    onError: (error) =>
      toast.error("Не удалось загрузить данные", {
        id: "query-error",
        description: apiErrorMessage(error),
      }),
  }),
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
})
