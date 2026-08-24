import { cn } from "@/shared/lib/utils"

import type { BenfordDetail } from "../model/types"

/** A digit whose share is off the law by more than this reads as a finding. */
const NOTABLE_DEVIATION = 0.02

const GRID_STEPS = [0, 0.5, 1]

/** Signed to one decimal, but never a signed zero: ±0.0 reads as a typo. */
function signed(value: number) {
  const shown = Math.abs(value).toFixed(1)
  if (shown === "0.0") return shown
  return `${value > 0 ? "+" : "−"}${shown}`
}

type Props = {
  data: BenfordDetail["distribution"]
  /** Taller plot for the case file, where the chart is the main exhibit. */
  tall?: boolean
}

/**
 * Observed first digits as bars, each against a tick at the frequency Benford's
 * law predicts — a control chart, read as "how far is this bar off its mark".
 */
export function BenfordPlot({ data, tall }: Props) {
  const plotHeight = tall ? "h-64" : "h-44"
  const ceiling =
    Math.max(...data.flatMap((d) => [d.empirical, d.theoretical])) * 1.12

  return (
    <figure className="flex flex-col gap-2">
      <div className="flex gap-3">
        <div className={cn("relative w-9 shrink-0", plotHeight)}>
          {GRID_STEPS.map((step) => (
            <span
              key={step}
              className="absolute right-0 translate-y-1/2 text-[0.625rem] leading-none text-muted-foreground tabular-nums"
              style={{ bottom: `${step * 100}%` }}
            >
              {Math.round(ceiling * step * 100)}%
            </span>
          ))}
        </div>

        <div className={cn("relative min-w-0 flex-1", plotHeight)}>
          {GRID_STEPS.map((step) => (
            <div
              key={step}
              aria-hidden
              className="absolute inset-x-0 border-t border-border/70"
              style={{ bottom: `${step * 100}%` }}
            />
          ))}

          <div className="absolute inset-0 grid grid-cols-9 items-end gap-[3px]">
            {data.map((d, i) => {
              const deviation = d.empirical - d.theoretical
              const notable = Math.abs(deviation) > NOTABLE_DEVIATION
              return (
                <div
                  key={d.digit}
                  className="relative h-full"
                  title={`Digit ${d.digit}: observed ${(d.empirical * 100).toFixed(1)}%, expected ${(d.theoretical * 100).toFixed(1)}%`}
                >
                  <div
                    className={cn(
                      "bar-rise absolute inset-x-0 bottom-0 rounded-t-[2px]",
                      notable ? "bg-destructive/80" : "bg-chart-observed"
                    )}
                    style={{
                      height: `${(d.empirical / ceiling) * 100}%`,
                      animationDelay: `${i * 40}ms`,
                    }}
                  />
                  <div
                    aria-hidden
                    className="absolute -inset-x-[3px] h-0.5 rounded-full bg-chart-expected"
                    style={{ bottom: `${(d.theoretical / ceiling) * 100}%` }}
                  />
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <div className="w-9 shrink-0" />
        <div className="grid min-w-0 flex-1 grid-cols-9 gap-[3px] border-t border-border pt-1.5">
          {data.map((d) => {
            const deviation = d.empirical - d.theoretical
            const notable = Math.abs(deviation) > NOTABLE_DEVIATION
            return (
              <div key={d.digit} className="flex flex-col items-center gap-0.5">
                <span className="text-[0.7rem] leading-none font-medium tabular-nums">
                  {d.digit}
                </span>
                <span
                  className={cn(
                    "text-[0.5625rem] leading-none tabular-nums",
                    notable ? "text-destructive" : "text-muted-foreground"
                  )}
                >
                  {signed(deviation * 100)}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      <figcaption className="eyebrow flex flex-wrap items-center gap-x-4 gap-y-1 pl-12">
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2 rounded-[1px] bg-chart-observed" />
          observed
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-3 rounded-full bg-chart-expected" />
          Benford
        </span>
        <span className="normal-case">
          deviation in percentage points, per digit
        </span>
      </figcaption>
    </figure>
  )
}
