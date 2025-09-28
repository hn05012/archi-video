export default function Loader({ label = 'Processing…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 text-white">
      <svg
        className="h-10 w-10 animate-spin"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        />
      </svg>
      <p className="text-sm opacity-80">{label}</p>
    </div>
  )
}
