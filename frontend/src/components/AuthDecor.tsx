// frontend/src/components/AuthDecor.tsx
function Leaf({
  x,
  y,
  rot,
  scale,
  filled = true,
}: {
  x: number
  y: number
  rot: number
  scale: number
  filled?: boolean
}) {
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${scale})`}>
      <path
        d="M0 0 C-38 -30 -42 -70 0 -100 C42 -70 38 -30 0 0Z"
        fill={filled ? '#A9CB9A' : 'none'}
        fillOpacity={filled ? 0.55 : 0}
        stroke="#7FAE70"
        strokeWidth="1.2"
        vectorEffect="non-scaling-stroke"
      />
      <g stroke="#7FAE70" strokeWidth="1" fill="none" opacity="0.8">
        <path d="M0 0 L0 -96" vectorEffect="non-scaling-stroke" />
        <path d="M0 -20 L-14 -34 M0 -20 L14 -34" vectorEffect="non-scaling-stroke" />
        <path d="M0 -45 L-17 -62 M0 -45 L17 -62" vectorEffect="non-scaling-stroke" />
        <path d="M0 -70 L-10 -82 M0 -70 L10 -82" vectorEffect="non-scaling-stroke" />
      </g>
    </g>
  )
}

export default function AuthDecor() {
  return (
    <>
      {/* bottom-left */}
      <svg
        className="pointer-events-none absolute bottom-0 left-0 h-auto w-[260px] sm:w-[340px] lg:w-[420px]"
        viewBox="0 0 400 520"
        aria-hidden="true"
      >
        <path d="M0 120 C90 90 190 170 190 300 C190 400 130 470 0 520Z" fill="#DDE9D2" fillOpacity="0.7" />
        <path d="M0 270 C120 250 270 340 400 520 L0 520Z" fill="#D3E3C6" fillOpacity="0.6" />
        <path d="M95 520 C92 440 90 400 88 330" stroke="#7FAE70" strokeWidth="1.2" fill="none" />
        <Leaf x={95} y={470} rot={-12} scale={2.2} />
        <Leaf x={150} y={510} rot={18} scale={1.6} filled={false} />
        <Leaf x={40} y={510} rot={-40} scale={1.5} />
      </svg>

      {/* top-right */}
      <svg
        className="pointer-events-none absolute right-0 top-0 h-auto w-[240px] sm:w-[320px] lg:w-[400px]"
        viewBox="0 0 400 480"
        aria-hidden="true"
      >
        <path d="M160 0 C170 110 280 150 400 140 L400 0Z" fill="#D8E6CC" fillOpacity="0.7" />
        <path d="M260 0 C290 70 340 100 400 100 L400 0Z" fill="#CDE0BF" fillOpacity="0.6" />
        <path d="M345 0 C350 90 360 160 380 240" stroke="#7FAE70" strokeWidth="1.2" fill="none" />
        <Leaf x={335} y={10} rot={172} scale={2.4} />
        <Leaf x={400} y={195} rot={100} scale={2.2} filled={false} />
        <Leaf x={372} y={120} rot={150} scale={1.3} />
      </svg>
    </>
  )
}