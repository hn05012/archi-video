import { z } from 'zod'

export const StartResponseSchema = z.union([
  z.object({ ok: z.literal(true), job_id: z.string() }),
  z.object({ ok: z.literal(false), error: z.string() }),
])
export type StartResponse = z.infer<typeof StartResponseSchema>

export type StartParams = {
  file: File

  num_frames?: number
  motion_bucket_id?: number

  frames?: number
  fps?: number
  max_side?: number
  steps?: number
  denoise_strength?: number
  cfg?: number
  seed?: number | null
  prompt?: string | null
  negative_prompt?: string | null
}

export const StatusResponseSchema = z.union([
  z.object({
    ok: z.literal(true),
    status: z.enum(['running', 'done', 'queued', 'failed']),
    progress: z
      .object({
        current: z.number().int(),
        total: z.number().int(),
        eta_seconds: z.number().nullable().optional(),
      })
      .optional(),
  }),
  z.object({ ok: z.literal(false), error: z.string() }),
])
export type StatusResponse = z.infer<typeof StatusResponseSchema>

export const ResultResponseSchema = z.union([
  z.object({
    ok: z.literal(true),
    src: z.string(),
    video_url: z.string(),
    download_url: z.string().optional(),
    meta: z
      .object({
        fps: z.number().int(),
        num_frames: z.number().int(),
        motion_bucket_id: z.number().int(),
        max_side: z.number().int(),
      })
      .optional(),
  }),
  z.object({ ok: z.literal(false), error: z.string() }),
])
export type ResultResponse = z.infer<typeof ResultResponseSchema>
