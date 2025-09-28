import { useState } from 'react'
import type { StartParams } from '../features/svd/schemas'

type Props = {
  onGenerate?: (params: StartParams) => void
}

export default function UploadImage({ onGenerate }: Props) {
  const [file, setFile] = useState<File | null>(null)

  const [frames, setFrames] = useState<number>(12)
  const [fps, setFps] = useState<number>(8)
  const [maxSide, setMaxSide] = useState<number>(352)
  const [steps, setSteps] = useState<number>(5)
  const [denoiseStrength, setDenoiseStrength] = useState<number>(0.6)
  const [cfg, setCfg] = useState<number>(1.2)
  const [seed, setSeed] = useState<number>(42)
  const [prompt, setPrompt] = useState<string>('')
  const [negativePrompt, setNegativePrompt] = useState<string>('')

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null
    setFile(f)
  }

  function submit() {
    if (!file) return
    onGenerate?.({
      file,
      frames,
      fps,
      max_side: maxSide,
      steps,
      denoise_strength: denoiseStrength,
      cfg,
      seed,
      prompt,
      negative_prompt: negativePrompt,
    })
  }

  return (
    <div className="w-full max-w-3xl">
      <div className="flex items-center gap-4 text-white">
        <label className="cursor-pointer rounded-xl bg-white/10 px-4 py-2 hover:bg-white/15">
          Upload Image
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={handleFile}
            className="hidden"
          />
        </label>

        {file && (
          <div className="min-w-0 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
            <div className="max-w-[60vw] truncate sm:max-w-md">{file.name}</div>
            <div className="text-xs text-white/50">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 grid grid-cols-2 gap-3 text-sm text-white">
        <label className="flex flex-col gap-1">
          <span>Frames</span>
          <input
            type="number"
            value={frames}
            onChange={(e) => setFrames(Number(e.target.value))}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>FPS</span>
          <input
            type="number"
            value={fps}
            onChange={(e) => setFps(Number(e.target.value))}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>Max side</span>
          <input
            type="number"
            value={maxSide}
            onChange={(e) => setMaxSide(Number(e.target.value))}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>Denoise steps</span>
          <input
            type="number"
            value={steps}
            onChange={(e) => setSteps(Number(e.target.value))}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>Denoise strength</span>
          <input
            type="number"
            step="0.05"
            value={denoiseStrength}
            onChange={(e) => setDenoiseStrength(Number(e.target.value))}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>CFG</span>
          <input
            type="number"
            step="0.1"
            value={cfg}
            onChange={(e) => setCfg(Number(e.target.value))}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>Seed</span>
          <input
            type="number"
            value={seed}
            onChange={(e) => setSeed(Number(e.target.value))}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="col-span-2 flex flex-col gap-1">
          <span>Prompt</span>
          <textarea
            rows={2}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
        <label className="col-span-2 flex flex-col gap-1">
          <span>Negative prompt</span>
          <textarea
            rows={2}
            value={negativePrompt}
            onChange={(e) => setNegativePrompt(e.target.value)}
            className="rounded-md bg-neutral-900 px-3 py-2"
          />
        </label>
      </div>

      {file && (
        <div className="mt-6">
          <button
            type="button"
            className="rounded-full bg-yellow-400 px-20 py-6 font-semibold text-black transition hover:bg-yellow-300 active:bg-yellow-500"
            onClick={submit}
          >
            Generate video
          </button>
        </div>
      )}
    </div>
  )
}
