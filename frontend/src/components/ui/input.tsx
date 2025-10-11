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
          'border border-gray-300',
          'bg-white px-4 py-2',
          'text-sm font-medium text-gray-900',
          'placeholder:text-gray-400 placeholder:font-normal',
          'transition-all duration-200',
          'hover:border-blue-400',
          'focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500',
          'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50',
          'file:border-0 file:bg-transparent file:text-sm file:font-semibold',
          'shadow-sm',
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
