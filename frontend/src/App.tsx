import UploadImage from './components/UploadImage'
import { useMutation, useQuery } from '@tanstack/react-query'
import { startSvd, getSvdStatus, getSvdResult } from './features/svd/api'
import type {
  StartResponse,
  StatusResponse,
  ResultResponse,
} from './features/svd/schemas'
import { use, useEffect, useState } from 'react'

export default function App() {
  const [jobId, setJobId] = useState<string | null>(null)

  const startMutation = useMutation<StartResponse, Error, File>({
    mutationFn: (file) => startSvd({ file }),
    onSuccess: (data) => {
      console.log('SVD start response: ', data)
      if (data.ok) setJobId(data.job_id)
    },
    onError: (err) => console.error('SVD start failed', err.message),
  })

  const statusQuery = useQuery<StatusResponse>({
    queryKey: ['svd-status', jobId],
    enabled: !!jobId,
    queryFn: () => getSvdStatus(jobId!),
    refetchInterval: (q) => {
      const d = q.state.data as StatusResponse | undefined
      return d && d.ok && (d.status === 'queued' || d.status === 'running')
        ? 2000
        : false
    },
  })

  const resultQuery = useQuery<ResultResponse>({
    queryKey: ['svd-result', jobId],
    enabled:
      !!jobId &&
      !!statusQuery.data &&
      statusQuery.data.ok &&
      statusQuery.data.status === 'done',
    queryFn: () => getSvdResult(jobId!),
    staleTime: Infinity,
  })

  useEffect(() => {
    if (statusQuery.data) console.log('SVD status: ', statusQuery.data)
  }, [statusQuery.data])

  useEffect(() => {
    if (resultQuery.data?.ok) {
      console.log('SVD Result:', resultQuery.data)
      console.log('Video URL:', resultQuery.data.video_url)
      console.log('Download URL: ', resultQuery.data.download_url)
    }
  }, [resultQuery.data])

  useEffect(() => {
    if (statusQuery.error) {
      const e = statusQuery.error as Error
      console.error('SVD status failed: ', e.message)
    }
  }, [statusQuery.error])

  return (
    <div className="min-h-screen bg-black">
      <header className="flex w-full justify-center pt-8">
        <h1 className="text-4xl font-bold text-white">ArchiVideo</h1>
      </header>
      <main className="flex justify-center pt-24">
        <UploadImage onGenerate={(file) => startMutation.mutate(file)} />
      </main>
    </div>
  )
}
