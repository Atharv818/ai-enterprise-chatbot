import { useId } from 'react'

export default function Logo({ size = 32 }: { size?: number }) {
  const uid = useId().replace(/:/g, '')
  const id = (name: string) => `${name}-${uid}`

  const leaves = [
    {
      key: 'top',
      d: 'M67.9 12.8 L63.4 15.0 L57.8 19.5 L55.0 23.1 L53.5 25.7 L52.0 29.3 L51.2 34.5 L50.5 36.6 L50.5 40.3 L51.6 45.0 L51.8 47.3 L52.7 49.5 L53.3 52.2 L56.3 58.2 L58.5 61.5 L61.7 65.3 L67.5 71.1 L72.2 75.4 L78.2 80.1 L85.2 86.7 L94.4 93.8 L96.1 95.5 L98.1 96.8 L98.9 97.0 L100.2 96.8 L111.3 87.6 L113.1 85.9 L117.3 82.7 L120.1 79.9 L124.0 76.9 L129.8 71.7 L135.3 65.7 L141.3 57.6 L144.3 51.6 L145.0 48.0 L146.3 43.5 L146.3 34.3 L144.5 27.6 L141.5 22.3 L137.0 17.3 L132.8 14.3 L129.3 12.6 L127.0 12.0 L125.1 12.0 L120.8 11.1 L118.6 11.1 L111.6 12.4 L108.4 13.9 L103.2 17.3 L98.9 21.8 L98.3 22.1 L93.4 17.1 L91.4 15.6 L85.0 12.4 L80.5 11.8 L74.9 11.6 L69.8 12.2Z',
    },
    {
      key: 'left',
      d: 'M31.0 62.7 L22.9 64.7 L16.7 68.3 L12.8 71.9 L10.9 74.7 L9.4 77.7 L8.1 82.0 L7.7 84.6 L7.9 89.9 L9.2 94.6 L10.7 97.9 L12.4 100.4 L14.8 103.2 L17.6 105.6 L17.3 106.6 L14.3 109.9 L10.9 115.8 L9.9 120.8 L9.6 124.0 L10.7 129.8 L12.0 133.0 L15.6 138.5 L18.2 141.1 L23.6 144.5 L27.2 146.0 L32.8 147.1 L37.9 147.3 L46.0 145.8 L50.5 144.1 L55.7 141.3 L60.2 137.9 L69.4 128.9 L88.2 108.4 L90.6 105.4 L91.0 103.9 L90.1 101.9 L87.8 99.1 L80.7 92.5 L78.2 89.7 L76.4 88.4 L65.7 78.4 L55.9 70.2 L48.6 66.0 L44.5 64.5 L37.0 62.7Z',
    },
    {
      key: 'right',
      d: 'M160.6 62.7 L153.1 64.7 L148.0 67.2 L146.9 67.5 L143.9 69.2 L139.4 72.4 L134.5 76.4 L132.5 78.6 L131.0 79.7 L119.3 91.2 L115.6 94.2 L110.7 99.1 L108.1 102.1 L107.5 103.6 L107.5 104.5 L108.6 106.4 L122.1 121.0 L127.4 126.1 L134.5 133.6 L138.5 136.8 L141.8 139.8 L147.1 143.0 L154.8 146.0 L159.5 146.9 L165.5 147.1 L172.2 146.0 L175.8 144.5 L179.0 142.6 L183.7 138.8 L187.4 133.6 L188.2 131.9 L189.9 125.9 L189.7 119.3 L188.4 115.0 L187.2 112.2 L185.0 109.0 L182.7 106.4 L182.2 105.1 L186.5 100.9 L187.8 98.9 L190.4 93.6 L191.4 89.1 L191.6 86.3 L190.6 80.5 L188.4 75.6 L185.9 71.9 L181.8 68.1 L176.4 64.9 L171.5 63.4 L167.9 62.7Z',
    },
    {
      key: 'bottom',
      d: 'M98.1 110.9 L97.0 111.6 L89.1 118.8 L86.3 121.0 L77.9 128.9 L66.4 141.1 L61.0 148.8 L58.2 155.2 L57.4 162.5 L57.4 166.2 L58.0 170.7 L59.5 174.9 L61.0 177.7 L62.7 179.9 L67.2 184.2 L72.2 186.9 L77.3 188.2 L79.4 188.2 L79.7 188.4 L84.2 188.2 L89.1 186.7 L92.1 185.2 L94.2 183.7 L99.6 178.4 L100.2 178.4 L105.4 183.7 L110.5 186.7 L112.2 187.4 L116.5 188.4 L122.1 188.4 L127.2 187.2 L133.2 183.9 L135.5 181.8 L139.4 176.9 L141.1 173.2 L142.2 169.4 L142.6 166.4 L142.4 160.2 L141.3 155.5 L140.5 154.0 L139.8 151.6 L137.3 146.7 L131.7 139.6 L110.9 119.7 L109.6 118.8 L106.0 115.4 L100.9 111.3 L100.0 110.9Z',
    },
  ]

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      aria-hidden="true"
      className="shrink-0"
    >
      <defs>
        {leaves.map((l) => (
          <path key={l.key} id={id(l.key)} d={l.d} />
        ))}

        <linearGradient
          id={id('base')}
          gradientUnits="userSpaceOnUse"
          x1="60"
          y1="10"
          x2="140"
          y2="190"
        >
          <stop offset="0" stopColor="#6FD654" />
          <stop offset="0.5" stopColor="#33A53E" />
          <stop offset="1" stopColor="#0C8537" />
        </linearGradient>

        {/* soft sheen over the top of the whole clover */}
        <linearGradient
          id={id('sheen')}
          gradientUnits="userSpaceOnUse"
          x1="0"
          y1="10"
          x2="0"
          y2="120"
        >
          <stop offset="0" stopColor="#FFFFFF" stopOpacity="0.05" />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
        </linearGradient>

        {/* glossy highlight blob */}
        <radialGradient id={id('gloss')}>
          <stop offset="0" stopColor="#FFFFFF" stopOpacity="0.10" />
          <stop offset="0.6" stopColor="#FFFFFF" stopOpacity="0.25" />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
        </radialGradient>

        <clipPath id={id('clip')}>
          {leaves.map((l) => (
            <use key={l.key} href={`#${id(l.key)}`} />
          ))}
        </clipPath>
      </defs>

      {/* base color */}
      <g fill={`url(#${id('base')})`}>
        {leaves.map((l) => (
          <use key={l.key} href={`#${id(l.key)}`} />
        ))}
      </g>

      {/* gloss, clipped to the leaves */}
      <g clipPath={`url(#${id('clip')})`}>
        <rect x="0" y="0" width="200" height="200" fill={`url(#${id('sheen')})`} />

        <g fill={`url(#${id('gloss')})`}>
          <ellipse cx="78" cy="33" rx="24" ry="12" transform="rotate(-32 78 33)" />
          <ellipse cx="32" cy="84" rx="21" ry="10" transform="rotate(-32 32 84)" />
          <ellipse cx="150" cy="83" rx="21" ry="10" transform="rotate(-32 150 83)" />
          <ellipse cx="80" cy="141" rx="17" ry="8" transform="rotate(-40 80 141)" />
        </g>
      </g>
    </svg>
  )
}