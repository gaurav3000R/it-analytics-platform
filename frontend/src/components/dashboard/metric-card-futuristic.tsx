import React from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
  color?: 'cyan' | 'purple' | 'pink' | 'green';
  loading?: boolean;
}

export const MetricCardFuturistic: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  icon,
  color = 'cyan',
  loading = false,
}) => {
  const gradients = {
    cyan: 'from-cyan-500/10 to-purple-500/10 border-cyan-500/20',
    purple: 'from-purple-500/10 to-pink-500/10 border-purple-500/20',
    pink: 'from-pink-500/10 to-purple-500/10 border-pink-500/20',
    green: 'from-green-500/10 to-emerald-500/10 border-green-500/20',
  };
  
  const iconColors = {
    cyan: 'text-cyan-400',
    purple: 'text-purple-400',
    pink: 'text-pink-400',
    green: 'text-green-400',
  };
  
  if (loading) {
    return (
      <div className={cn(
        'relative rounded-2xl p-6',
        'bg-gradient-to-br backdrop-blur-xl border',
        'overflow-hidden animate-pulse',
        gradients[color]
      )}>
        <div className="h-4 bg-white/10 rounded w-1/2 mb-4" />
        <div className="h-8 bg-white/10 rounded w-3/4 mb-2" />
        <div className="h-3 bg-white/10 rounded w-1/3" />
      </div>
    );
  }
  
  return (
    <div className={cn(
      'relative rounded-2xl p-6',
      'bg-gradient-to-br backdrop-blur-xl border',
      'overflow-hidden transition-all duration-300',
      'hover:scale-[1.02] hover:-translate-y-1',
      gradients[color]
    )}>
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.1) 2px, rgba(255,255,255,0.1) 4px)`
        }} />
      </div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <span className={cn('text-sm font-medium', iconColors[color])}>
            {title}
          </span>
          {icon && (
            <div className={cn('p-2 rounded-lg bg-white/5', iconColors[color])}>
              {icon}
            </div>
          )}
        </div>
        
        <div className="text-white text-3xl font-bold mb-2">
          {value}
        </div>
        
        {change !== undefined && (
          <div className={cn(
            'flex items-center gap-1 text-xs font-medium',
            change >= 0 ? 'text-green-400' : 'text-red-400'
          )}>
            {change >= 0 ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            <span>{Math.abs(change)}% from last period</span>
          </div>
        )}
      </div>
    </div>
  );
};
