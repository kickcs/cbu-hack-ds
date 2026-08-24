import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { Toaster } from "sonner"

import "./styles/index.css"
import { QueryProvider } from "./providers/query-provider"
import { AppRoutes } from "./routes"
import { RouterProvider } from "@/shared/lib/router"
import { ThemeProvider } from "@/shared/lib/theme"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="light" storageKey="regtech-theme">
      <QueryProvider>
        <RouterProvider>
          <AppRoutes />
        </RouterProvider>
      </QueryProvider>
      <Toaster position="top-right" richColors />
    </ThemeProvider>
  </StrictMode>
)
