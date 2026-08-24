export type Meta = {
  banks: string[]
  register_rows: number
  min_sample: number
  insufficient: string[]
  normativ_rows: number
  report_rows: number
}

export type RunResult = {
  run_id: number
  total_banks: number
  suspicious_banks: string[]
  result_file: string
  natija_file: string
}
