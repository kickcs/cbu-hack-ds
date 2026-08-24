/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react"

import { testCell, type BankAudit } from "@/entities/bank"

type BankFiltersState = {
  query: string
  setQuery: (value: string) => void
  flaggedOnly: boolean
  toggleFlaggedOnly: () => void
  /** Tests the view is narrowed to; empty means every test. */
  tests: string[]
  toggleTest: (test: string) => void
  clear: () => void
  active: boolean
  filter: (rows: BankAudit[]) => BankAudit[]
}

const BankFiltersContext = createContext<BankFiltersState | undefined>(
  undefined
)

export function BankFiltersProvider({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("")
  const [flaggedOnly, setFlaggedOnly] = useState(false)
  const [tests, setTests] = useState<string[]>([])

  const toggleTest = useCallback((test: string) => {
    setTests((current) =>
      current.includes(test)
        ? current.filter((t) => t !== test)
        : [...current, test]
    )
  }, [])

  const clear = useCallback(() => {
    setQuery("")
    setFlaggedOnly(false)
    setTests([])
  }, [])

  const value = useMemo<BankFiltersState>(() => {
    const needle = query.trim().toLowerCase()
    return {
      query,
      setQuery,
      flaggedOnly,
      toggleFlaggedOnly: () => setFlaggedOnly((v) => !v),
      tests,
      toggleTest,
      clear,
      active: needle !== "" || flaggedOnly || tests.length > 0,
      filter: (rows) =>
        rows.filter((row) => {
          if (flaggedOnly && !row.suspicious) return false
          if (needle && !row.bank.toLowerCase().includes(needle)) return false
          if (tests.length && !tests.some((t) => testCell(row, t).flagged)) {
            return false
          }
          return true
        }),
    }
  }, [query, flaggedOnly, tests, toggleTest, clear])

  return (
    <BankFiltersContext.Provider value={value}>
      {children}
    </BankFiltersContext.Provider>
  )
}

export function useBankFilters(): BankFiltersState {
  const context = useContext(BankFiltersContext)
  if (context === undefined) {
    throw new Error("useBankFilters must be used within a BankFiltersProvider")
  }
  return context
}
