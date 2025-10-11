import React from 'react';
import { cn } from '@/lib/utils';

interface RoughPaperCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'subtle' | 'bold';
  color?: 'blue' | 'purple' | 'green' | 'amber' | 'pink';
}

/**
 * RoughPaperCard - A card component with a blurry, textured paper-like effect
 * Perfect for creating a modern, organic design aesthetic
 */
export const RoughPaperCard: React.FC<RoughPaperCardProps> = ({
  children,
  className,
  variant = 'default',
  color = 'blue',
}) => {
  const colorVariants = {
    blue: 'bg-gradient-to-br from-blue-50 via-white to-blue-50/50',
    purple: 'bg-gradient-to-br from-purple-50 via-white to-purple-50/50',
    green: 'bg-gradient-to-br from-green-50 via-white to-green-50/50',
    amber: 'bg-gradient-to-br from-amber-50 via-white to-amber-50/50',
    pink: 'bg-gradient-to-br from-pink-50 via-white to-pink-50/50',
  };

  const variantStyles = {
    default: 'backdrop-blur-sm',
    subtle: 'backdrop-blur-md',
    bold: 'backdrop-blur-lg',
  };

  return (
    <div
      className={cn(
        'relative rounded-2xl p-6 overflow-hidden',
        'border border-gray-200/80',
        'shadow-md hover:shadow-lg',
        'transition-all duration-300',
        colorVariants[color],
        variantStyles[variant],
        className
      )}
      style={{
        filter: 'blur(0px) contrast(1.02)',
      }}
    >
      {/* Rough paper texture overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='3.5' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundSize: '180px 180px',
        }}
      />
      
      {/* Subtle gradient shimmer */}
      <div 
        className="absolute inset-0 opacity-[0.15] pointer-events-none mix-blend-overlay"
        style={{
          background: 'linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 50%, rgba(255,255,255,0.8) 100%)',
          backgroundSize: '200% 200%',
        }}
      />
      
      {/* Rough edge effect */}
      <div 
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          boxShadow: 'inset 0 0 20px rgba(0,0,0,0.02)',
        }}
      />
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

export default RoughPaperCard;
