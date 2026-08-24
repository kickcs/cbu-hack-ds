import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { auditApi, auditKeys } from "@/entities/audit"
import { bankKeys } from "@/entities/bank"
import { apiErrorMessage } from "@/shared/api/client"

export function useRunAudit() {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: auditApi.run,
    onSuccess: async (result) => {
      const flagged = result.suspicious_banks.length
      toast.success("Audit complete", {
        description: flagged
          ? `${flagged} of ${result.total_banks} banks flagged.`
          : `No findings across ${result.total_banks} banks.`,
      })
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: auditKeys.all }),
        queryClient.invalidateQueries({ queryKey: bankKeys.all }),
      ])
    },
    onError: (error) =>
      toast.error("Audit failed to run", {
        description: apiErrorMessage(error),
      }),
  })

  return { running: isPending, run: mutate }
}
