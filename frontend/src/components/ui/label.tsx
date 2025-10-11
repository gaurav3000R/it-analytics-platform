import * as React from 'react'
import { cn } from '@/lib/utils'

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, required, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(
          'text-sm font-semibold text-gray-700',
          'leading-none',
          'peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
          'block mb-2',
          className
        )}
        {...props}
      >
        {children}
        {required && <span className="text-red-500 ml-1 font-bold">*</span>}
      </label>
    )
  }
)
Label.displayName = 'Label'

export { Label }
