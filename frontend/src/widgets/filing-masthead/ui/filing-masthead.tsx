import {
  DocketRule,
  docketNo,
  filedAt,
  tookFor,
  STATUS_NOTES,
  STATUS_LABELS,
  type FilingReport,
} from "@/entities/submission"
import { fmtCount } from "@/shared/lib/format"
import { cn } from "@/shared/lib/utils"
import { Reading } from "@/shared/ui/reading"

/** The cover of one filing: what came in, and what the examination made of it. */
export function FilingMasthead({ filing }: { filing: FilingReport }) {
  const flagged = filing.suspicious_count ?? 0
  const took = tookFor(filing.started_at, filing.finished_at)

  return (
    <section className="flex gap-5">
      <DocketRule status={filing.status} flagged={flagged > 0} />

      <div className="flex min-w-0 flex-1 flex-col gap-4">
        <p className="eyebrow">
          Filing {docketNo(filing.id)} · filed {filedAt(filing.created_at)}
        </p>

        <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
          {filing.title}
        </h1>

        <p className="max-w-2xl text-base leading-relaxed text-pretty">
          {summary(filing)}
        </p>

        <dl className="grid grid-cols-2 gap-x-6 gap-y-5 border-t pt-4 sm:grid-cols-4 sm:gap-x-10">
          <Reading label="Banks read" emphasis>
            {filing.total_banks === null ? "—" : fmtCount(filing.total_banks)}
          </Reading>
          <Reading label="Flagged" emphasis>
            <span className={cn(flagged > 0 && "text-destructive")}>
              {filing.status === "done" ? flagged : "—"}
            </span>
          </Reading>
          <Reading label="Files" emphasis>
            {filing.files.length}
          </Reading>
          <Reading label="Examined in" emphasis>
            {took ?? STATUS_LABELS[filing.status]}
          </Reading>
        </dl>

        <FileList files={filing.files} />
      </div>
    </section>
  )
}

function summary(filing: FilingReport): string {
  if (filing.status !== "done") {
    return filing.error ?? STATUS_NOTES[filing.status]
  }

  const flagged = filing.suspicious_count ?? 0
  const banks = filing.total_banks ?? 0
  const scope = `${fmtCount(banks)} ${banks === 1 ? "bank" : "banks"}`

  return flagged === 0
    ? `Nothing in this filing crossed a threshold. ${scope} were read and every test they carried input for came back clean.`
    : `${flagged} of ${scope} in this filing crossed at least one threshold. They are ranked below, worst first.`
}

/** What was actually in the envelope, and what intake took each file for. */
function FileList({ files }: { files: FilingReport["files"] }) {
  return (
    <ul className="flex flex-col gap-1 border-t pt-4">
      {files.map((file) => (
        <li
          key={file.sha256}
          className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5 text-xs"
        >
          <span className="code min-w-0 flex-1 truncate text-foreground">
            {file.name}
          </span>
          <span
            className={cn(
              "shrink-0",
              file.role === "unknown"
                ? "text-muted-foreground/70"
                : "text-muted-foreground"
            )}
          >
            {file.role_label}
          </span>
          <span className="w-20 shrink-0 text-right text-muted-foreground tabular-nums">
            {file.rows > 0 ? `${fmtCount(file.rows)} rows` : "—"}
          </span>
        </li>
      ))}
    </ul>
  )
}
