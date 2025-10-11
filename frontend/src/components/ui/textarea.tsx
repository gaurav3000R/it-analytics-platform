import * as React from 'react'
import { cn } from '@/lib/utils'

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          'flex min-h-[100px] w-full rounded-lg',
          'border border-gray-200',
          'bg-white px-4 py-3',
          'text-sm font-medium text-gray-900 leading-relaxed',
          'placeholder:text-gray-500 placeholder:font-normal',
          'transition-all duration-200',
          'hover:border-gray-300',
          'focus:outline-none focus:ring-2 focus:ring-cyan-500/20 focus:border-cyan-500',
          'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50',
          'resize-y',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = 'Textarea'

export { Textarea }
