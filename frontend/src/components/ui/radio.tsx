import * as React from 'react'
import { cn } from '@/lib/utils'

export interface RadioProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

const Radio = React.forwardRef<HTMLInputElement, RadioProps>(
  ({ className, label, id, ...props }, ref) => {
    const radioId = id || `radio-${Math.random().toString(36).substr(2, 9)}`
    
    return (
      <div className="flex items-center">
        <input
          type="radio"
          id={radioId}
          className={cn(
            'h-4 w-4 rounded-full',
            'border border-gray-300',
            'bg-white',
            'text-cyan-600',
            'transition-colors duration-200',
            'hover:border-cyan-400',
            'focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'cursor-pointer',
            className
          )}
          ref={ref}
          {...props}
        />
        {label && (
          <label
            htmlFor={radioId}
            className="ml-2 text-sm text-gray-700 cursor-pointer select-none"
          >
            {label}
          </label>
        )}
      </div>
    )
  }
)
Radio.displayName = 'Radio'

export { Radio }
