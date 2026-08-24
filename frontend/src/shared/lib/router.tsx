/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ComponentProps,
} from "react"

type Navigate = (to: string, options?: { replace?: boolean }) => void

type RouterState = {
  path: string
  navigate: Navigate
}

const RouterContext = createContext<RouterState | null>(null)

/**
 * Two routes and a back link do not need a routing library. Real paths (not a
 * hash) because both the dev server and nginx already fall back to index.html.
 */
export function RouterProvider({ children }: { children: React.ReactNode }) {
  const [path, setPath] = useState(() => window.location.pathname)

  useEffect(() => {
    const sync = () => setPath(window.location.pathname)
    window.addEventListener("popstate", sync)
    return () => window.removeEventListener("popstate", sync)
  }, [])

  const navigate = useCallback<Navigate>((to, { replace } = {}) => {
    if (to === window.location.pathname) return
    window.history[replace ? "replaceState" : "pushState"](null, "", to)
    setPath(to)
    window.scrollTo({ top: 0 })
  }, [])

  const value = useMemo(() => ({ path, navigate }), [path, navigate])

  return (
    <RouterContext.Provider value={value}>{children}</RouterContext.Provider>
  )
}

function useRouter(): RouterState {
  const router = useContext(RouterContext)
  if (!router) throw new Error("useRouter must be used inside RouterProvider")
  return router
}

export function usePath(): string {
  return useRouter().path
}

export function useNavigate(): Navigate {
  return useRouter().navigate
}

/** Modified clicks stay with the browser, so open-in-new-tab keeps working. */
function handledLocally(event: React.MouseEvent) {
  return (
    event.button === 0 &&
    !event.metaKey &&
    !event.ctrlKey &&
    !event.shiftKey &&
    !event.altKey &&
    !event.defaultPrevented
  )
}

export function Link({
  to,
  replace,
  onClick,
  ...props
}: Omit<ComponentProps<"a">, "href"> & { to: string; replace?: boolean }) {
  const navigate = useNavigate()

  return (
    <a
      href={to}
      onClick={(event) => {
        onClick?.(event)
        if (!handledLocally(event)) return
        event.preventDefault()
        navigate(to, { replace })
      }}
      {...props}
    />
  )
}
