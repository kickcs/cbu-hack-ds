import { MoonIcon, SunIcon } from "lucide-react"

import { useTheme } from "@/shared/lib/theme"
import { Button } from "@/shared/ui/button"

export function ThemeToggle() {
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
      title="Switch theme (D)"
    >
      {dark ? <SunIcon /> : <MoonIcon />}
      <span className="sr-only">Switch to {dark ? "light" : "dark"} theme</span>
    </Button>
  )
}
