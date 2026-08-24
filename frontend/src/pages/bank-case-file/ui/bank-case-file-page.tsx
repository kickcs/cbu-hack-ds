import { ArrowLeftIcon, ArrowRightIcon, ChevronLeftIcon } from "lucide-react"
import { useTranslation } from "react-i18next"

import type { BankAudit } from "@/entities/bank"
import { RunAuditButton } from "@/features/run-audit"
import { ThemeToggle } from "@/features/theme-toggle"
import { Link } from "@/shared/lib/router"
import { bankPath, DASHBOARD_PATH } from "@/shared/lib/routes"
import { Skeleton } from "@/shared/ui/skeleton"
import { AppHeader } from "@/widgets/app-header"
import { BenfordReport } from "@/widgets/benford-report"
import { CaseFileMasthead } from "@/widgets/case-file-masthead"
import { EvidenceLog } from "@/widgets/evidence-log"
import { TestRoster } from "@/widgets/test-roster"

import { useCaseFile } from "../model/use-case-file"

/**
 * One bank, at full page width: the verdict, the tests behind it, and the
 * figures behind those. The exception matrix says which banks to read; this
 * page is the reading.
 */
export function BankCaseFilePage({ bank }: { bank: string }) {
  const { t } = useTranslation("app")
  const file = useCaseFile(bank)

  return (
    <div className="min-h-svh bg-background text-foreground">
      <AppHeader>
        <ThemeToggle />
        <RunAuditButton />
      </AppHeader>

      <CaseFileNav previous={file.previous} next={file.next} />

      <main className="mx-auto flex max-w-6xl flex-col gap-10 px-5 py-8 sm:px-8">
        {file.listLoading && <LoadingFile />}

        {file.missing && <NoCaseFile bank={bank} />}

        {file.audit && (
          <>
            <CaseFileMasthead
              audit={file.audit}
              rank={file.rank}
              total={file.total}
              cells={file.cells}
              records={file.detail?.n ?? null}
            />

            <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_23rem]">
              <aside className="lg:col-start-2 lg:row-start-1">
                <div className="lg:sticky lg:top-28 lg:max-h-[calc(100svh-9rem)] lg:overflow-y-auto">
                  <TestRoster cells={file.cells} />
                </div>
              </aside>

              <div className="flex flex-col gap-10 lg:col-start-1 lg:row-start-1">
                {file.detailFailed && !file.detailLoading && (
                  <p className="border-l-2 border-destructive py-1 pl-4 text-sm text-muted-foreground">
                    <span className="font-medium text-destructive">
                      {t("caseFile.detailUnavailable")}
                    </span>{" "}
                    {t("caseFile.detailUnavailableBody")}
                  </p>
                )}

                {file.detailLoading && <LoadingDetail />}

                {file.detail && !file.detailLoading && (
                  <BenfordReport detail={file.detail} />
                )}

                {file.evidence && !file.detailLoading && (
                  <EvidenceLog evidence={file.evidence} />
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}

function CaseFileNav({
  previous,
  next,
}: {
  previous: BankAudit | null
  next: BankAudit | null
}) {
  const { t } = useTranslation("app")

  return (
    <nav
      aria-label={t("caseFile.navLabel")}
      className="sticky top-14 z-10 border-b bg-background/90 backdrop-blur"
    >
      <div className="mx-auto flex h-11 max-w-6xl items-center justify-between gap-4 px-5 sm:px-8">
        <Link
          to={DASHBOARD_PATH}
          className="code flex items-center gap-1 rounded-sm text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
        >
          <ChevronLeftIcon className="size-3" />
          {t("caseFile.allBanks")}
        </Link>

        <div className="flex min-w-0 items-center gap-4">
          <StepLink audit={previous} direction="previous" />
          <span className="h-4 w-px bg-border" aria-hidden />
          <StepLink audit={next} direction="next" />
        </div>
      </div>
    </nav>
  )
}

/** Walking the ranked list without going back to the matrix each time. */
function StepLink({
  audit,
  direction,
}: {
  audit: BankAudit | null
  direction: "previous" | "next"
}) {
  const { t } = useTranslation("app")
  const Icon = direction === "previous" ? ArrowLeftIcon : ArrowRightIcon

  if (!audit) {
    return (
      <span className="flex items-center gap-1.5 text-xs text-muted-foreground/50">
        {direction === "previous" && <Icon className="size-3" />}
        {direction === "previous"
          ? t("caseFile.firstInRank")
          : t("caseFile.lastInRank")}
        {direction === "next" && <Icon className="size-3" />}
      </span>
    )
  }

  return (
    <Link
      to={bankPath(audit.bank)}
      className="flex min-w-0 items-center gap-1.5 rounded-sm text-xs text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
    >
      {direction === "previous" && <Icon className="size-3 shrink-0" />}
      <span className="truncate">{audit.bank}</span>
      {direction === "next" && <Icon className="size-3 shrink-0" />}
    </Link>
  )
}

function NoCaseFile({ bank }: { bank: string }) {
  const { t } = useTranslation("app")

  return (
    <section className="flex flex-col items-start gap-4 border-l-2 border-border pl-5">
      <p className="eyebrow">{t("caseFile.title")}</p>
      <h1 className="font-display text-2xl font-semibold tracking-tight">
        {t("caseFile.noFileFor", { bank })}
      </h1>
      <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
        {t("caseFile.noFileBody")}
      </p>
      <Link
        to={DASHBOARD_PATH}
        className="code rounded-sm text-foreground underline underline-offset-4 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
      >
        {t("caseFile.backToAllBanks")}
      </Link>
    </section>
  )
}

function LoadingFile() {
  return (
    <div className="flex flex-col gap-6">
      <Skeleton className="h-3 w-32" />
      <Skeleton className="h-10 w-80 max-w-full" />
      <Skeleton className="h-4 w-full max-w-xl" />
      <Skeleton className="h-16 w-full max-w-lg" />
    </div>
  )
}

function LoadingDetail() {
  return (
    <div className="flex flex-col gap-4">
      <Skeleton className="h-3 w-40" />
      <Skeleton className="h-72 w-full" />
      <Skeleton className="h-32 w-full" />
    </div>
  )
}
