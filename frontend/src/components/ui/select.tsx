import * as React from 'react'
import { cn } from '@/lib/utils'

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <select
        className={cn(
          'flex h-10 w-full rounded-lg',
          'border border-gray-200',
          'bg-white px-3 py-2 pr-8',
          'text-sm text-gray-900',
          'transition-all duration-200',
          'hover:border-gray-300',
          'focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500',
          'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50',
          'appearance-none',
          'bg-[url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%236b7280\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")]',
          'bg-[length:1.25rem] bg-[right_0.5rem_center] bg-no-repeat',
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </select>
    )
  }
)
Select.displayName = 'Select'

export { Select }
