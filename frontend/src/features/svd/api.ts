import { API_BASE_URL } from '../../lib/env'
import { postForm } from '../../lib/http'
import {
  StatusResponseSchema,
  type StartParams,
  StartResponseSchema,
  type StartResponse,
  type StatusResponse,
  type ResultResponse,
  ResultResponseSchema,
} from './schemas'
import { getJson } from '../../lib/http'

export async function startSvd(
  params: StartParams,
  signal?: AbortSignal,
): Promise<StartResponse> {
  const {
    file,
    num_frames = 16,
    fps = 8,
    motion_bucket_id = 100,
    max_side = 512,
    seed = 42,
  } = params

  const formData = new FormData()

  formData.append('file', file)
  formData.append('num_frames', String(num_frames))
  formData.append('fps', String(fps))
  formData.append('motion_bucket_id', String(motion_bucket_id))
  formData.append('max_side', String(max_side))
  formData.append('seed', String(seed))

  const url = new URL('/colab/svd/start', API_BASE_URL).toString()

  const raw = await postForm<unknown>(url, formData, signal)

  const parsed = StartResponseSchema.safeParse(raw)

  if (!parsed.success) throw new Error('Unexpected /colab/svd/start response')

  return parsed.data
}

export async function getSvdStatus(
  jobId: string,
  signal?: AbortSignal,
): Promise<StatusResponse> {
  const url = new URL(
    `/colab/svd/status/${encodeURIComponent(jobId)}`,
    API_BASE_URL,
  ).toString()

  const raw = await getJson<unknown>(url, signal)

  const parsed = StatusResponseSchema.safeParse(raw)

  if (!parsed.success) throw new Error('Unexpected /colab/svd/status response')

  return parsed.data
}

export async function getSvdResult(
  jobId: string,
  signal?: AbortSignal,
): Promise<ResultResponse> {
  const url = new URL(
    `/colab/svd/result/${encodeURIComponent(jobId)}`,
    API_BASE_URL,
  ).toString()
  const raw = await getJson<unknown>(url, signal)
  const parsed = ResultResponseSchema.safeParse(raw)
  if (!parsed.success) throw new Error('Unexpected /colab/svd/result response')
  return parsed.data
}
