import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { Toaster } from "sonner"

import "./styles/index.css"
import { QueryProvider } from "./providers/query-provider"
import { ThemeProvider } from "@/shared/lib/theme"
import { DashboardPage } from "@/pages/dashboard"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="light" storageKey="regtech-theme">
      <QueryProvider>
        <DashboardPage />
      </QueryProvider>
      <Toaster position="top-right" richColors />
    </ThemeProvider>
  </StrictMode>
)
