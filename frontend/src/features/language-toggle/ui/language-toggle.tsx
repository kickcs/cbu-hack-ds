import { useTranslation } from "react-i18next"

import { setLanguage, SUPPORTED_LANGUAGES } from "@/shared/lib/i18n"
import { cn } from "@/shared/lib/utils"
import { Button } from "@/shared/ui/button"

/** EN / RU / UZ — the only controls that are never translated themselves. */
export function LanguageToggle() {
  const { i18n, t } = useTranslation("ui")

  return (
    <div
      role="group"
      aria-label={t("language.label")}
      className="flex items-center gap-0.5"
    >
      {SUPPORTED_LANGUAGES.map((code) => (
        <Button
          key={code}
          variant="ghost"
          size="xs"
          aria-pressed={i18n.language === code}
          onClick={() => setLanguage(code)}
          className={cn(
            "text-[0.7rem] font-semibold tracking-widest",
            i18n.language === code
              ? "text-foreground"
              : "text-muted-foreground"
          )}
        >
          {code.toUpperCase()}
        </Button>
      ))}
    </div>
  )
}
