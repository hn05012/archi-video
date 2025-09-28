import UploadImage from './components/UploadImage'
import Loader from './components/Loader'
import VideoPlayer from './components/VideoPlayer'

import { useMutation, useQuery } from '@tanstack/react-query'
import { startSvd, getSvdStatus, getSvdResult } from './features/svd/api'
import type {
  StartResponse,
  StatusResponse,
  ResultResponse,
  StartParams,
} from './features/svd/schemas'
import { useEffect, useMemo, useState } from 'react'
import { API_BASE_URL } from './lib/env'

export default function App() {
  const [jobId, setJobId] = useState<string | null>(null)

  const startMutation = useMutation<StartResponse, Error, StartParams>({
    mutationFn: (params) => startSvd(params),
    onSuccess: (data) => {
      const anyData = data as any
      const id =
        (anyData.ok ? anyData.job_id : null) ??
        (typeof anyData.job_id === 'string' ? anyData.job_id : null)
      if (id) setJobId(id)
    },
  })

  const statusQuery = useQuery<StatusResponse>({
    queryKey: ['svd-status', jobId],
    enabled: !!jobId,
    queryFn: () => getSvdStatus(jobId!),
    refetchInterval: (q) => {
      const d = q.state.data as StatusResponse | undefined
      const status = (d as any)?.status
      const ok = (d as any)?.ok ?? true
      return ok && (status === 'queued' || status === 'running') ? 2000 : false
    },
  })

  const resultQuery = useQuery<ResultResponse>({
    queryKey: ['svd-result', jobId],
    enabled:
      !!jobId &&
      !!statusQuery.data &&
      (statusQuery.data as any).status === 'done',
    queryFn: () => getSvdResult(jobId!),
    staleTime: Infinity,
  })

  useEffect(() => {
    if (statusQuery.data) console.log('SVD status: ', statusQuery.data)
  }, [statusQuery.data])

  useEffect(() => {
    if (resultQuery.data) console.log('SVD Result:', resultQuery.data)
  }, [resultQuery.data])

  const resolvedVideoUrl = useMemo(() => {
    const data = resultQuery.data as any
    if (!data || data.ok === false) return null
    let url: string | undefined = data.video_url ?? data.src ?? data.video_path
    if (!url) return null
    try {
      new URL(url)
    } catch {
      url = new URL(url.replace(/^\//, ''), API_BASE_URL).toString()
    }
    return url
  }, [resultQuery.data])

  const status = (statusQuery.data as any)?.status as
    | 'queued'
    | 'running'
    | 'done'
    | 'failed'
    | undefined

  const prog = (statusQuery.data as any)?.progress as
    | { current?: number; total?: number; eta_seconds?: number }
    | undefined

  const isLoadingVideo =
    !!jobId && (status === 'queued' || status === 'running')

  return (
    <div className="min-h-screen bg-black">
      <header className="flex w-full justify-center pt-8">
        <h1 className="text-4xl font-bold text-white">ArchiVideo</h1>
      </header>

      <main className="flex justify-center pt-12">
        <div className="w-full max-w-3xl px-6">
          {!jobId && (
            <UploadImage
              onGenerate={(params) => startMutation.mutate(params)}
            />
          )}

          {jobId && isLoadingVideo && (
            <div className="mt-16">
              <Loader label="Generating video on CPU…" />
              <p className="mt-4 text-center text-xs text-white/60">
                job: {jobId} — status: {status}
              </p>
            </div>
          )}

          {jobId && status === 'done' && resolvedVideoUrl && (
            <div className="mt-10">
              <VideoPlayer src={resolvedVideoUrl} />
              <p className="mt-4 text-center text-xs text-white/60">
                job: {jobId} — finished
              </p>
            </div>
          )}

          {jobId && status === 'failed' && (
            <p className="mt-10 text-center text-rose-300">
              Generation failed. Please try again.
            </p>
          )}
        </div>
      </main>
    </div>
  )
}
