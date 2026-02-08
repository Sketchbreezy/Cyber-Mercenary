import { HTMLAttributes, forwardRef } from 'react';
import { cn } from './Button';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: 'default' | 'success' | 'warning' | 'danger';
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
    ({ className, variant = 'default', ...props }, ref) => {
        return (
            <span
                ref={ref}
                className={cn(
                    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
                    {
                        'bg-primary/10 text-primary border border-primary/20': variant === 'default',
                        'bg-success/10 text-success border border-success/20': variant === 'success',
                        'bg-warning/10 text-warning border border-warning/20': variant === 'warning',
                        'bg-accent/10 text-accent border border-accent/20': variant === 'danger',
                    },
                    className
                )}
                {...props}
            />
        );
    }
);

Badge.displayName = 'Badge';

export { Badge };
