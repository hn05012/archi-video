import { useId, useState } from 'react'

type Props = {
  onFileSelected?: (file: File) => void
  onGenerate?: (file: File) => void
}

export default function UploadImage({ onFileSelected, onGenerate }: Props) {
  // const inputId = useId();
  const [file, setFile] = useState<File | null>(null)

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null
    setFile(f)
    if (f && onFileSelected) onFileSelected(f)
  }

  return (
    <div>
      <div className="flex items-center gap-4 text-white">
        <label className="cursor-pointer rounded-xl bg-white/10 px-4 py-2 hover:bg-white/15">
          Upload Image
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={handleChange}
            className="hidden"
          />
        </label>

        {file && (
          <div
            className="min-w-0 rounded-lg border border-white/10 bg-white/5 px-3 py-2"
            title={file.name}
          >
            <div className="max-w-[60vw] truncate sm:max-w-md">{file.name}</div>
            <div className="text-xs text-white/50">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </div>
          </div>
        )}
      </div>

      {file && (
        <div className="mt-6 flex items-start">
          <button
            type="button"
            className="rounded-full bg-yellow-400 px-20 py-6 font-semibold text-black transition hover:bg-yellow-300 active:bg-yellow-500"
            onClick={() => onGenerate?.(file)}
          >
            Generate video
          </button>
        </div>
      )}
    </div>
  )
}
