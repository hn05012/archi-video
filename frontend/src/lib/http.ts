export class HttpError extends Error {
  public status: number
  public data?: unknown

  constructor(message: string, status: number, data?: unknown) {
    super(message)
    this.name = 'HttpError'
    this.status = status
    this.data = data
  }
}

export async function postForm<T>(
  url: string,
  form: FormData,
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(url, { method: 'POST', body: form, signal })
  const text = await response.text()

  let data: unknown = null

  try {
    data = text ? JSON.parse(text) : null
  } catch {}

  if (!response.ok) {
    const message =
      (data as any)?.error ||
      (data as any)?.message ||
      `HTTP ${response.status}`

    throw new HttpError(message, response.status, data)
  }

  return data as T
}

export async function getJson<T>(
  url: string,
  signal?: AbortSignal,
): Promise<T> {
  const res = await fetch(url, { method: 'GET', signal })
  const text = await res.text()

  let data: unknown = null

  try {
    data = text ? JSON.parse(text) : null
  } catch {}

  if (!res.ok) {
    const msg =
      (data as any)?.error || (data as any)?.message || `HTTP ${res.status}`
    throw new HttpError(msg, res.status, data)
  }

  return data as T
}
