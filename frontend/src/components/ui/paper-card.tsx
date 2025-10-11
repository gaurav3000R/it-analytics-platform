import * as React from 'react'
import { cn } from '@/lib/utils'

const PaperCard = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    variant?: 'default' | 'subtle' | 'vibrant'
  }
>(({ className, variant = 'default', children, ...props }, ref) => {
  const variants = {
    default: 'before:from-blue-100/40 before:via-cyan-50/30 before:to-purple-100/40',
    subtle: 'before:from-gray-50/60 before:via-white/50 before:to-gray-100/60',
    vibrant: 'before:from-cyan-100/50 before:via-blue-50/40 before:to-purple-100/50'
  }

  return (
    <div
      ref={ref}
      className={cn(
        'relative overflow-hidden rounded-xl',
        'bg-white/80 backdrop-blur-sm',
        'border border-gray-200/80',
        'shadow-lg',
        // Paper texture effect
        'before:absolute before:inset-0',
        'before:bg-gradient-to-br',
        variants[variant],
        'before:opacity-50',
        'before:blur-3xl',
        'before:pointer-events-none',
        // Rough edges effect
        'after:absolute after:inset-0',
        'after:bg-[url("data:image/svg+xml,%3Csvg viewBox=\'0 0 400 400\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' /%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\' opacity=\'0.03\'/%3E%3C/svg%3E")]',
        'after:pointer-events-none',
        'after:mix-blend-overlay',
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
PaperCard.displayName = 'PaperCard'

const PaperCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
))
PaperCardHeader.displayName = 'PaperCardHeader'

const PaperCardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-2xl font-semibold leading-none tracking-tight text-gray-900', className)}
    {...props}
  />
))
PaperCardTitle.displayName = 'PaperCardTitle'

const PaperCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-600', className)}
    {...props}
  />
))
PaperCardDescription.displayName = 'PaperCardDescription'

const PaperCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
))
PaperCardContent.displayName = 'PaperCardContent'

const PaperCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
))
PaperCardFooter.displayName = 'PaperCardFooter'

export {
  PaperCard,
  PaperCardHeader,
  PaperCardTitle,
  PaperCardDescription,
  PaperCardContent,
  PaperCardFooter
}
