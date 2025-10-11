import * as React from 'react'
import { cn } from '@/lib/utils'

const FrostedCard = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    intensity?: 'light' | 'medium' | 'strong'
  }
>(({ className, intensity = 'medium', children, ...props }, ref) => {
  const intensityClasses = {
    light: 'bg-white/60 backdrop-blur-md border-gray-200/60',
    medium: 'bg-white/70 backdrop-blur-lg border-gray-200/70',
    strong: 'bg-white/80 backdrop-blur-xl border-gray-200/80'
  }

  return (
    <div
      ref={ref}
      className={cn(
        'relative overflow-hidden rounded-2xl',
        intensityClasses[intensity],
        'border shadow-xl',
        // Gradient overlay for depth
        'before:absolute before:inset-0',
        'before:bg-gradient-to-br before:from-white/20 before:via-transparent before:to-cyan-100/20',
        'before:pointer-events-none',
        // Subtle grain texture
        'after:absolute after:inset-0',
        'after:bg-[url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'3\' numOctaves=\'3\' /%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\' opacity=\'0.02\'/%3E%3C/svg%3E")]',
        'after:pointer-events-none',
        // Hover effect
        'transition-all duration-300',
        'hover:shadow-2xl hover:scale-[1.01]',
        'hover:border-cyan-300/50',
        className
      )}
      {...props}
    >
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
})
FrostedCard.displayName = 'FrostedCard'

const FrostedCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
))
FrostedCardHeader.displayName = 'FrostedCardHeader'

const FrostedCardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-2xl font-semibold leading-none tracking-tight text-gray-900', className)}
    {...props}
  />
))
FrostedCardTitle.displayName = 'FrostedCardTitle'

const FrostedCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-600', className)}
    {...props}
  />
))
FrostedCardDescription.displayName = 'FrostedCardDescription'

const FrostedCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
))
FrostedCardContent.displayName = 'FrostedCardContent'

const FrostedCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
))
FrostedCardFooter.displayName = 'FrostedCardFooter'

export {
  FrostedCard,
  FrostedCardHeader,
  FrostedCardTitle,
  FrostedCardDescription,
  FrostedCardContent,
  FrostedCardFooter
}
