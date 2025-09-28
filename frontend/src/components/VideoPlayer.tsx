type Props = {
  src: string
  className?: string
}

export default function VideoPlayer({ src, className }: Props) {
  return (
    <div className={`flex flex-col items-center gap-4 ${className ?? ''}`}>
      <video
        key={src}
        src={src}
        className="max-h-[70vh] max-w-[90vw] rounded-lg shadow-lg"
        controls
        playsInline
        loop
        autoPlay
        muted
        controlsList="nodownload noplaybackrate"
        onContextMenu={(e) => e.preventDefault()}
      />
    </div>
  )
}
