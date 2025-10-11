import React from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  neonBorder?: 'cyan' | 'purple' | 'pink' | 'none';
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className,
  hover = true,
  neonBorder = 'none',
}) => {
  const borderColors = {
    cyan: 'hover:border-cyan-400 hover:shadow-lg hover:shadow-cyan-500/20',
    purple: 'hover:border-purple-400 hover:shadow-lg hover:shadow-purple-500/20',
    pink: 'hover:border-pink-400 hover:shadow-lg hover:shadow-pink-500/20',
    none: '',
  };
  
  return (
    <div
      className={cn(
        'rounded-2xl p-6',
        'bg-white/90 backdrop-blur-2xl',
        'border border-gray-200',
        'shadow-sm',
        hover && 'transition-all duration-300 hover:bg-white hover:-translate-y-1 hover:shadow-md',
        neonBorder !== 'none' && borderColors[neonBorder],
        className
      )}
    >
      {children}
    </div>
  );
};
