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
    cyan: 'hover:border-cyan-500/50 hover:shadow-[0_0_20px_rgba(0,245,255,0.4)]',
    purple: 'hover:border-purple-500/50 hover:shadow-[0_0_20px_rgba(168,85,247,0.4)]',
    pink: 'hover:border-pink-500/50 hover:shadow-[0_0_20px_rgba(236,72,153,0.4)]',
    none: '',
  };
  
  return (
    <div
      className={cn(
        'rounded-2xl p-6',
        'bg-white/[0.05] backdrop-blur-2xl',
        'border border-white/10',
        hover && 'transition-all duration-300 hover:bg-white/[0.08] hover:-translate-y-1',
        neonBorder !== 'none' && borderColors[neonBorder],
        className
      )}
    >
      {children}
    </div>
  );
};
