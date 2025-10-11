import * as React from 'react'
import { cn } from '@/lib/utils'

const TexturedCard = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    texture?: 'paper' | 'canvas' | 'linen' | 'grain'
  }
>(({ className, texture = 'paper', children, ...props }, ref) => {
  const textures = {
    paper: {
      bg: 'bg-white',
      pattern: 'before:bg-gradient-to-br before:from-amber-50/30 before:via-white/20 before:to-blue-50/30',
      noise: 'after:bg-[url("data:image/svg+xml,%3Csvg viewBox=\'0 0 400 400\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noise\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' /%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noise)\' opacity=\'0.03\'/%3E%3C/svg%3E")]'
    },
    canvas: {
      bg: 'bg-gradient-to-br from-gray-50 to-white',
      pattern: 'before:bg-[url("data:image/svg+xml,%3Csvg width=\'20\' height=\'20\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23d1d5db\' fill-opacity=\'0.05\' fill-rule=\'evenodd\'%3E%3Ccircle cx=\'3\' cy=\'3\' r=\'3\'/%3E%3Ccircle cx=\'13\' cy=\'13\' r=\'3\'/%3E%3C/g%3E%3C/svg%3E")]',
      noise: 'after:bg-gradient-to-br after:from-transparent after:via-gray-100/20 after:to-transparent'
    },
    linen: {
      bg: 'bg-white',
      pattern: 'before:bg-[url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23e5e7eb\' fill-opacity=\'0.08\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")]',
      noise: ''
    },
    grain: {
      bg: 'bg-white',
      pattern: 'before:bg-gradient-to-br before:from-blue-50/40 before:via-transparent before:to-purple-50/40',
      noise: 'after:bg-[url("data:image/svg+xml,%3Csvg viewBox=\'0 0 300 300\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'grain\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'1.5\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23grain)\' opacity=\'0.04\'/%3E%3C/svg%3E")]'
    }
  }

  const selectedTexture = textures[texture]

  return (
    <div
      ref={ref}
      className={cn(
        'relative overflow-hidden rounded-xl',
        selectedTexture.bg,
        'border border-gray-200',
        'shadow-md',
        // Background pattern layer
        'before:absolute before:inset-0',
        selectedTexture.pattern,
        'before:pointer-events-none',
        'before:blur-2xl',
        // Texture/noise layer
        'after:absolute after:inset-0',
        selectedTexture.noise,
        'after:pointer-events-none',
        'after:mix-blend-multiply',
        // Hover effect
        'transition-all duration-300',
        'hover:shadow-lg hover:border-gray-300',
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
TexturedCard.displayName = 'TexturedCard'

const TexturedCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
))
TexturedCardHeader.displayName = 'TexturedCardHeader'

const TexturedCardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-2xl font-semibold leading-none tracking-tight text-gray-900', className)}
    {...props}
  />
))
TexturedCardTitle.displayName = 'TexturedCardTitle'

const TexturedCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-600', className)}
    {...props}
  />
))
TexturedCardDescription.displayName = 'TexturedCardDescription'

const TexturedCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
))
TexturedCardContent.displayName = 'TexturedCardContent'

const TexturedCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
))
TexturedCardFooter.displayName = 'TexturedCardFooter'

export {
  TexturedCard,
  TexturedCardHeader,
  TexturedCardTitle,
  TexturedCardDescription,
  TexturedCardContent,
  TexturedCardFooter
}
