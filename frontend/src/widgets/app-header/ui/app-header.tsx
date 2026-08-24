import type { ReactNode } from "react"
import { useTranslation } from "react-i18next"

import { BenfordMark } from "@/entities/bank"
import { LanguageToggle } from "@/features/language-toggle"

/** Masthead of a filed report: who issued it, and the controls for re-issuing it. */
export function AppHeader({ children }: { children: ReactNode }) {
  const { t } = useTranslation("app")

  return (
    <header className="sticky top-0 z-20 border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-5 sm:px-8">
        <div className="flex items-center gap-3">
          <BenfordMark className="h-5 text-foreground" />
          <span className="h-6 w-px bg-border" aria-hidden />
          <div className="leading-tight">
            <p className="font-display text-sm font-bold tracking-tight">
              {t("header.brand")}
            </p>
            <p className="eyebrow">{t("header.tagline")}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <LanguageToggle />
          {children}
        </div>
      </div>
    </header>
  )
}
