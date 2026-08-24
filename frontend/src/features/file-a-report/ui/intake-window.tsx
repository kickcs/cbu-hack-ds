import { useRef, useState } from "react"

import { cn } from "@/shared/lib/utils"
import { Button } from "@/shared/ui/button"

import { useFileAReport } from "../model/use-file-a-report"

const ACCEPT = ".csv,.xlsx,.xml"

/**
 * The intake desk: choose files first, then send them as one filing with a
 * dedicated button. Nothing starts the moment a file is picked -- the auditor
 * gets to see what is queued up and drop anything picked by mistake.
 */
export function IntakeWindow() {
  const { filing, file } = useFileAReport()
  const [pending, setPending] = useState<File[]>([])
  const [over, setOver] = useState(false)
  const input = useRef<HTMLInputElement>(null)

  function addFiles(files: FileList | null) {
    const chosen = Array.from(files ?? [])
    if (chosen.length === 0) return
    setPending((prev) => [...prev, ...chosen])
    if (input.current) input.current.value = ""
  }

  function remove(index: number) {
    setPending((prev) => prev.filter((_, i) => i !== index))
  }

  function submit() {
    if (pending.length === 0 || filing) return
    file(pending, { onSuccess: () => setPending([]) })
  }

  return (
    <section className="overflow-hidden rounded-lg border bg-card">
      <label
        onDragOver={(event) => {
          event.preventDefault()
          setOver(true)
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(event) => {
          event.preventDefault()
          setOver(false)
          addFiles(event.dataTransfer.files)
        }}
        className={cn(
          "group relative block cursor-pointer overflow-hidden px-5 py-8 text-center transition-colors sm:px-8",
          "bg-[repeating-linear-gradient(to_bottom,transparent_0_1.5rem,var(--band)_1.5rem_3rem)]",
          "focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background",
          over ? "border-destructive/60" : "hover:border-foreground/25",
          filing && "pointer-events-none opacity-60"
        )}
      >
        <span aria-hidden className="absolute inset-x-0 top-0 h-0.5 bg-destructive transition-transform duration-150" style={{ transform: over ? "scaleX(1)" : "scaleX(0)" }} />

        <input
          ref={input}
          type="file"
          multiple
          accept={ACCEPT}
          disabled={filing}
          onChange={(event) => addFiles(event.target.files)}
          className="sr-only"
        />

        <span className="eyebrow block">Upload Report</span>

        <span className="mt-2 block font-display text-lg font-semibold tracking-tight sm:text-xl">
          Drop files here, or click to choose
        </span>

        <span className="code mt-3 block text-muted-foreground">
          CSV · XLSX · XML — up to 25 MB each
        </span>

        <span className="mx-auto mt-4 block max-w-md text-xs leading-relaxed text-balance text-muted-foreground">
          Choose any number of files, review them below, then send them as one
          filing. Nothing is examined until you press the button.
        </span>
      </label>

      {pending.length > 0 && (
        <div className="border-t px-5 py-4">
          <ul className="flex flex-col gap-1.5">
            {pending.map((entry, i) => (
              <li
                key={`${entry.name}-${entry.lastModified}-${i}`}
                className="flex items-center gap-3 text-sm"
              >
                <span className="min-w-0 flex-1 truncate font-medium">
                  {entry.name}
                </span>
                <span className="code shrink-0 text-muted-foreground">
                  {fileSize(entry.size)}
                </span>
                <button
                  type="button"
                  onClick={() => remove(i)}
                  disabled={filing}
                  className="code shrink-0 rounded-sm px-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-destructive focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none disabled:pointer-events-none"
                >
                  remove
                </button>
              </li>
            ))}
          </ul>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p className="code text-xs text-muted-foreground">
              {pending.length} file{pending.length === 1 ? "" : "s"} ready
            </p>
            <Button onClick={submit} disabled={filing}>
              {filing ? "Sending the filing…" : "Upload Report"}
            </Button>
          </div>
        </div>
      )}
    </section>
  )
}

function fileSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}
