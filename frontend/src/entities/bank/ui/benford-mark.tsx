import { cn } from "@/shared/lib/utils"

// log10(1 + 1/d) for d = 1..9 — the silhouette of Benford's law, and the mark
// this report files under.
const BENFORD_HEIGHTS = Array.from({ length: 9 }, (_, i) =>
  Math.log10(1 + 1 / (i + 1))
)

const MAX = BENFORD_HEIGHTS[0]

export function BenfordMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 98 62"
      aria-hidden
      className={cn("h-full w-auto", className)}
    >
      {BENFORD_HEIGHTS.map((h, i) => {
        const barHeight = (h / MAX) * 58
        return (
          <rect
            key={i}
            className="bar-rise"
            x={i * 11}
            y={60 - barHeight}
            width={7}
            height={barHeight}
            rx={1}
            fill="currentColor"
            style={{ animationDelay: `${i * 55}ms` }}
          />
        )
      })}
    </svg>
  )
}
