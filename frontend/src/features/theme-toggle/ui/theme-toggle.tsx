import { MoonIcon, SunIcon } from "lucide-react"
import { useTranslation } from "react-i18next"

import { useTheme } from "@/shared/lib/theme"
import { Button } from "@/shared/ui/button"

export function ThemeToggle() {
  const { t } = useTranslation("ui")
  const { theme, setTheme } = useTheme()
  const dark =
    theme === "dark" ||
    (theme === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches)

  return (
    <Button
      variant="ghost"
      size="icon-sm"
      onClick={() => setTheme(dark ? "light" : "dark")}
      title={t("theme.switchTitle")}
    >
      {dark ? <SunIcon /> : <MoonIcon />}
      <span className="sr-only">
        {dark ? t("theme.toLight") : t("theme.toDark")}
      </span>
    </Button>
  )
}
