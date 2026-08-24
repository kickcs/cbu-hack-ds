import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { docketNo, submissionApi, submissionKeys } from "@/entities/submission"
import { apiErrorMessage } from "@/shared/api/client"
import i18n from "@/shared/lib/i18n"

export function useFileAReport() {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: submissionApi.upload,
    onSuccess: async (filing) => {
      toast.success(
        i18n.t("ui:toast.filingReceived", { docket: docketNo(filing.id) }),
        {
          description: i18n.t("ui:toast.filingQueued"),
        }
      )
      await queryClient.invalidateQueries({ queryKey: submissionKeys.all })
    },
    // A rejected upload is the auditor's to fix, so it says what was wrong with the file.
    onError: (error) =>
      toast.error(i18n.t("ui:toast.filingRejected"), {
        description: apiErrorMessage(error),
      }),
  })

  return { filing: isPending, file: mutate }
}
