import { ButtonHTMLAttributes, forwardRef } from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:pointer-events-none disabled:opacity-50',
                    {
                        'bg-primary text-background hover:bg-primary/90 shadow-[0_0_10px_rgba(0,240,255,0.3)] hover:shadow-[0_0_15px_rgba(0,240,255,0.5)]':
                            variant === 'primary',
                        'bg-secondary text-white hover:bg-secondary/90 shadow-[0_0_10px_rgba(112,0,255,0.3)]':
                            variant === 'secondary',
                        'border border-primary/50 text-primary hover:bg-primary/10':
                            variant === 'outline',
                        'hover:bg-white/10 text-white': variant === 'ghost',
                        'bg-accent text-white hover:bg-accent/90 shadow-[0_0_10px_rgba(255,0,60,0.3)]':
                            variant === 'danger',
                        'h-8 px-3 text-xs': size === 'sm',
                        'h-10 px-4 py-2': size === 'md',
                        'h-12 px-6 text-lg': size === 'lg',
                    },
                    className
                )}
                {...props}
            />
        );
    }
);

Button.displayName = 'Button';

export { Button, cn };
