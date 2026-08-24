import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { auditApi, auditKeys } from "@/entities/audit"
import { bankKeys } from "@/entities/bank"
import { apiErrorMessage } from "@/shared/api/client"
import i18n from "@/shared/lib/i18n"

export function useRunAudit() {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: auditApi.run,
    onSuccess: async (result) => {
      const flagged = result.suspicious_banks.length
      toast.success(i18n.t("ui:toast.auditComplete"), {
        description: flagged
          ? i18n.t("ui:toast.flaggedOf", {
              flagged,
              total: result.total_banks,
            })
          : i18n.t("ui:toast.noFindingsAcross", {
              total: result.total_banks,
            }),
      })
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: auditKeys.all }),
        queryClient.invalidateQueries({ queryKey: bankKeys.all }),
      ])
    },
    onError: (error) =>
      toast.error(i18n.t("ui:toast.auditFailed"), {
        description: apiErrorMessage(error),
      }),
  })

  return { running: isPending, run: mutate }
}
