import { z } from 'zod'

export const StartResponseSchema = z.union([
  z.object({ ok: z.literal(true), job_id: z.string() }),
  z.object({ ok: z.literal(false), error: z.string() }),
])

export type StartResponse = z.infer<typeof StartResponseSchema>

export type StartParams = {
  file: File
  num_frames?: number
  fps?: number
  motion_bucket_id?: number
  max_side?: number
  seed?: number
}

export const StatusResponseSchema = z.union([
  z.object({
    ok: z.literal(true),
    status: z.enum(['running', 'done', 'queued']),
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
