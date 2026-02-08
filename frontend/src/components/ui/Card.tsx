import { HTMLAttributes, forwardRef } from 'react';
import { cn } from './Button'; // Reuse cn utility

const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
    ({ className, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    'glass-panel rounded-lg p-6 text-text-primary',
                    className
                )}
                {...props}
            />
        );
    }
);

Card.displayName = 'Card';

export { Card };
