import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { docketNo, submissionApi, submissionKeys } from "@/entities/submission"
import { apiErrorMessage } from "@/shared/api/client"

/** Removing one filing takes its stored files with it; there is no undo. */
export function useDiscardFiling() {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: submissionApi.remove,
    onSuccess: async (_, id) => {
      toast.success(`Filing ${docketNo(id)} discarded`)
      await queryClient.invalidateQueries({ queryKey: submissionKeys.all })
    },
    onError: (error) =>
      toast.error("Filing not discarded", {
        description: apiErrorMessage(error),
      }),
  })

  return { discarding: isPending, discard: mutate }
}

export function useClearDocket() {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: submissionApi.clear,
    onSuccess: async ({ deleted }) => {
      toast.success(
        deleted === 1 ? "1 filing discarded" : `${deleted} filings discarded`,
        { description: "The supervisory dataset is untouched." }
      )
      await queryClient.invalidateQueries({ queryKey: submissionKeys.all })
    },
    onError: (error) =>
      toast.error("Docket not cleared", {
        description: apiErrorMessage(error),
      }),
  })

  return { clearing: isPending, clear: mutate }
}
