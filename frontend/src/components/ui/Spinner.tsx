import { cn } from './Button';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <svg
      className={cn('animate-spin text-primary', sizeClasses[size], className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
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
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export function PageLoader() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <div className="relative">
        <div className="w-16 h-16 rounded-full border-2 border-primary/20" />
        <div className="absolute top-0 left-0 w-16 h-16 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      </div>
      <p className="text-text-muted font-mono text-sm animate-pulse">INITIALIZING...</p>
    </div>
  );
}

export function ScanLoader() {
  return (
    <div className="flex flex-col items-center justify-center py-12 space-y-6">
      <div className="relative w-32 h-32">
        <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
        <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin" />
        <div className="absolute inset-4 border-4 border-secondary/20 rounded-full" />
        <div className="absolute inset-4 border-4 border-secondary rounded-full border-b-transparent animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1s' }} />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 bg-primary rounded-full animate-ping" />
        </div>
      </div>
      <div className="text-center space-y-2">
        <p className="text-lg font-bold text-white">SCANNING CONTRACT</p>
        <p className="text-sm text-text-muted font-mono">Analyzing bytecode & storage...</p>
      </div>
      <div className="w-64 h-1 bg-surface rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-primary to-secondary animate-progress" style={{ width: '60%' }} />
      </div>
    </div>
  );
}
