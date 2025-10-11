import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  glowEffect?: boolean;
}

export const ButtonFuturistic: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  glowEffect = false,
  className,
  ...props
}) => {
  const baseClasses = 'relative inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300 overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white hover:scale-105 hover:shadow-[0_0_20px_rgba(0,245,255,0.6)]',
    secondary: 'bg-white/5 backdrop-blur-xl border border-white/10 text-white hover:bg-white/10 hover:border-cyan-500/50',
    ghost: 'bg-transparent text-cyan-400 hover:bg-cyan-500/10',
    outline: 'bg-transparent border-2 border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-400',
  };
  
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };
  
  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        glowEffect && 'animate-glow-pulse',
        className
      )}
      {...props}
    >
      {variant === 'primary' && (
        <div className="absolute inset-0 bg-white opacity-0 hover:opacity-20 transition-opacity duration-300" />
      )}
      <span className="relative z-10">{children}</span>
    </button>
  );
};
