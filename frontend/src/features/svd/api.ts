import { API_BASE_URL } from '../../lib/env'
import { postForm, getJson } from '../../lib/http'
import {
  StartResponseSchema,
  type StartParams,
  type StartResponse,
  StatusResponseSchema,
  type StatusResponse,
  ResultResponseSchema,
  type ResultResponse,
} from './schemas'

function toAbsoluteUrl(url: string): string {
  try {
    new URL(url)
    return url
  } catch {
    return new URL(url.replace(/^\//, ''), API_BASE_URL).toString()
  }
}

export async function startSvd(
  params: StartParams,
  signal?: AbortSignal,
): Promise<StartResponse> {
  const {
    file,

    num_frames,
    fps = 9,
    max_side = 320,
    seed = 42,

    frames,
    steps = 6,
    denoise_strength = 0.4,
    cfg = 1.0,

    prompt,
    negative_prompt,
  } = params as any

  const effFrames = frames ?? num_frames ?? 20

  const formData = new FormData()
  formData.append('image', file)
  formData.append('frames', String(effFrames))
  formData.append('fps', String(fps))
  formData.append('max_side', String(max_side))
  formData.append('steps', String(steps))
  formData.append('denoise_strength', String(denoise_strength))
  formData.append('cfg', String(cfg))
  formData.append('seed', String(seed))
  if (prompt) formData.append('prompt', String(prompt))
  if (negative_prompt)
    formData.append('negative_prompt', String(negative_prompt))

  const url = new URL('/svd/', API_BASE_URL).toString()
  const raw = await postForm<any>(url, formData, signal)

  if (raw && typeof raw === 'object' && typeof raw.job_id === 'string') {
    return { ok: true, job_id: raw.job_id } as StartResponse
  }

  const parsed = StartResponseSchema.safeParse(raw)
  if (!parsed.success) {
    throw new Error('Unexpected /svd/ start response')
  }
  return parsed.data
}

export async function getSvdStatus(
  jobId: string,
  signal?: AbortSignal,
): Promise<StatusResponse> {
  const url = new URL(
    `/svd/status/${encodeURIComponent(jobId)}`,
    API_BASE_URL,
  ).toString()
  const raw = await getJson<any>(url, signal)

  if (
    raw &&
    typeof raw === 'object' &&
    typeof raw.status === 'string' &&
    !('ok' in raw)
  ) {
    return {
      ok: true,
      status: raw.status,
      progress: raw.progress,
    } as StatusResponse
  }

  const parsed = StatusResponseSchema.safeParse(raw)
  if (!parsed.success) {
    throw new Error('Unexpected /svd/status response')
  }
  return parsed.data
}

export async function getSvdResult(
  jobId: string,
  signal?: AbortSignal,
): Promise<ResultResponse> {
  const url = new URL(
    `/svd/result/${encodeURIComponent(jobId)}`,
    API_BASE_URL,
  ).toString()
  const raw = await getJson<any>(url, signal)

  if (raw && typeof raw === 'object' && raw.video_path) {
    const abs = toAbsoluteUrl(String(raw.video_path))
    const meta = raw.params ?? {}
    const mapped: ResultResponse = {
      ok: true,
      src: abs,
      video_url: abs,
      meta: {
        fps: Number(raw.fps ?? meta.fps ?? 9),
        num_frames: Number(raw.frames ?? meta.frames ?? 20),
        motion_bucket_id: Number(meta.motion_bucket_id ?? 0),
        max_side: Number(meta.max_side ?? raw.max_side ?? 320),
      },
    }
    const parsed = ResultResponseSchema.safeParse(mapped)
    if (!parsed.success) return mapped
    return parsed.data
  }

  const parsed = ResultResponseSchema.safeParse(raw)
  if (!parsed.success) {
    throw new Error('Unexpected /svd/result response')
  }
  return parsed.data
}
