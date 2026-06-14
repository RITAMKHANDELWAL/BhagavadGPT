import { cn } from '~/utils/';

export default function BhagvadGPTIcon({
    size = 25,
    className = '',
}: {
    size?: number;
    className?: string;
}) {
    const height = size;
    const width = size;

    return (
        <svg
            width={width}
            height={height}
            viewBox="0 0 100 100"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={cn(className, '')}
            aria-hidden="true"
        >
            <defs>
                <linearGradient id="bhagvadGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{ stopColor: '#FF9933', stopOpacity: 1 }} />
                    <stop offset="50%" style={{ stopColor: '#FFA500', stopOpacity: 1 }} />
                    <stop offset="100%" style={{ stopColor: '#FF8C00', stopOpacity: 1 }} />
                </linearGradient>
            </defs>

            {/* Om Symbol simplified for small icon */}
            <g transform="translate(50, 50)">
                {/* Main curve */}
                <path
                    d="M -20,-15 Q -25,-10 -25,-2 Q -25,5 -20,10 Q -15,15 -8,15 Q 0,15 5,10 Q 10,5 10,-2 L 10,-15"
                    fill="none"
                    stroke="url(#bhagvadGradient)"
                    strokeWidth="4"
                    strokeLinecap="round"
                />

                {/* Top curve */}
                <path
                    d="M -10,-20 Q 0,-25 10,-20"
                    fill="none"
                    stroke="url(#bhagvadGradient)"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                />

                {/* Right curve */}
                <path
                    d="M 15,-10 Q 20,-5 20,2 Q 20,10 15,15"
                    fill="none"
                    stroke="url(#bhagvadGradient)"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                />

                {/* Bottom dot */}
                <circle cx="0" cy="23" r="3" fill="url(#bhagvadGradient)" />

                {/* Center spiral */}
                <path
                    d="M 0,-5 Q 5,-5 5,0 Q 5,5 0,5 Q -5,5 -5,0 Q -5,-5 0,-5"
                    fill="none"
                    stroke="url(#bhagvadGradient)"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                />
            </g>
        </svg>
    );
}
