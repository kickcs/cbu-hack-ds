import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { docketNo, submissionApi, submissionKeys } from "@/entities/submission"
import { apiErrorMessage } from "@/shared/api/client"

export function useFileAReport() {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: submissionApi.upload,
    onSuccess: async (filing) => {
      toast.success(`Filing ${docketNo(filing.id)} received`, {
        description:
          "It is in the queue. The docket updates as it is examined.",
      })
      await queryClient.invalidateQueries({ queryKey: submissionKeys.all })
    },
    // A rejected upload is the auditor's to fix, so it says what was wrong with the file.
    onError: (error) =>
      toast.error("Filing not accepted", {
        description: apiErrorMessage(error),
      }),
  })

  return { filing: isPending, file: mutate }
}
