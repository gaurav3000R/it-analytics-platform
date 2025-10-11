import * as React from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-11 w-full rounded-lg',
          'border border-gray-200',
          'bg-white px-4 py-2',
          'text-sm font-medium text-gray-900',
          'placeholder:text-gray-500 placeholder:font-normal',
          'transition-all duration-200',
          'hover:border-gray-300',
          'focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500',
          'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50',
          'file:border-0 file:bg-transparent file:text-sm file:font-semibold',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input }
