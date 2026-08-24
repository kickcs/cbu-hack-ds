import { useQuery } from "@tanstack/react-query"
import { ChevronLeftIcon } from "lucide-react"
import { useTranslation } from "react-i18next"

import { filingsQuery } from "@/entities/submission"
import { IntakeWindow } from "@/features/file-a-report"
import { ThemeToggle } from "@/features/theme-toggle"
import { Link } from "@/shared/lib/router"
import { DASHBOARD_PATH } from "@/shared/lib/routes"
import { AppHeader } from "@/widgets/app-header"
import { DocketList } from "@/widgets/docket-list"

/**
 * The intake desk: hand a filing in at the top, watch it move down the docket
 * below. Nothing filed here touches the supervisory dataset.
 */
export function FilingsPage() {
  const { t } = useTranslation("app")
  const { data, isPending } = useQuery(filingsQuery())

  return (
    <div className="min-h-svh bg-background text-foreground">
      <AppHeader>
        <ThemeToggle />
      </AppHeader>

      <nav
        aria-label={t("filings.navLabel")}
        className="sticky top-14 z-10 border-b bg-background/90 backdrop-blur"
      >
        <div className="mx-auto flex h-11 max-w-6xl items-center px-5 sm:px-8">
          <Link
            to={DASHBOARD_PATH}
            className="code flex items-center gap-1 rounded-sm text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
          >
            <ChevronLeftIcon className="size-3" />
            {t("filings.supervisoryDataset")}
          </Link>
        </div>
      </nav>

      <main className="mx-auto flex max-w-6xl flex-col gap-10 px-5 py-8 sm:px-8">
        <header className="flex flex-col gap-3 border-l-2 pl-5">
          <p className="eyebrow">{t("filings.uploadReport")}</p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
            {t("filings.title")}
          </h1>
          <p className="max-w-2xl text-base leading-relaxed text-pretty">
            {t("filings.intro")}
          </p>
        </header>

        <IntakeWindow />

        <DocketList filings={data ?? []} loading={isPending} />
      </main>
    </div>
  )
}
