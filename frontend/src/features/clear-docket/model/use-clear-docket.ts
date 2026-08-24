import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { docketNo, submissionApi, submissionKeys } from "@/entities/submission"
import { apiErrorMessage } from "@/shared/api/client"
import i18n from "@/shared/lib/i18n"

/** Removing one filing takes its stored files with it; there is no undo. */
export function useDiscardFiling() {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: submissionApi.remove,
    onSuccess: async (_, id) => {
      toast.success(
        i18n.t("ui:toast.filingDiscarded", { docket: docketNo(id) })
      )
      await queryClient.invalidateQueries({ queryKey: submissionKeys.all })
    },
    onError: (error) =>
      toast.error(i18n.t("ui:toast.filingNotDiscarded"), {
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
      toast.success(i18n.t("ui:toast.filingsDiscarded", { count: deleted }), {
        description: i18n.t("ui:toast.supervisoryUntouched"),
      })
      await queryClient.invalidateQueries({ queryKey: submissionKeys.all })
    },
    onError: (error) =>
      toast.error(i18n.t("ui:toast.docketNotCleared"), {
        description: apiErrorMessage(error),
      }),
  })

  return { clearing: isPending, clear: mutate }
}
