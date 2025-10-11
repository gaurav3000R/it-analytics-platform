import React from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  subtitle?: string;
  icon?: React.ReactNode;
  color?: 'cyan' | 'purple' | 'pink' | 'green';
  loading?: boolean;
}

export const MetricCardFuturistic: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  subtitle,
  icon,
  color = 'cyan',
  loading = false,
}) => {
  const gradients = {
    cyan: 'bg-cyan-50/80 border-cyan-100',
    purple: 'bg-purple-50/80 border-purple-100',
    pink: 'bg-pink-50/80 border-pink-100',
    green: 'bg-green-50/80 border-green-100',
  };
  
  const iconColors = {
    cyan: 'text-cyan-600',
    purple: 'text-purple-600',
    pink: 'text-pink-600',
    green: 'text-green-600',
  };
  
  const iconBgColors = {
    cyan: 'bg-cyan-100',
    purple: 'bg-purple-100',
    pink: 'bg-pink-100',
    green: 'bg-green-100',
  };
  
  if (loading) {
    return (
      <div className={cn(
        'relative rounded-2xl p-6',
        'backdrop-blur-xl border-2',
        'overflow-hidden animate-pulse',
        'shadow-sm',
        gradients[color]
      )}>
        <div className="h-4 bg-gray-300 rounded w-1/2 mb-4" />
        <div className="h-8 bg-gray-300 rounded w-3/4 mb-2" />
        <div className="h-3 bg-gray-300 rounded w-1/3" />
      </div>
    );
  }
  
  return (
    <div className={cn(
      'relative rounded-2xl p-6',
      'backdrop-blur-xl border-2',
      'overflow-hidden transition-all duration-300',
      'hover:scale-[1.02] hover:-translate-y-1',
      'shadow-sm hover:shadow-lg',
      gradients[color]
    )}>
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.05) 2px, rgba(0,0,0,0.05) 4px)`
        }} />
      </div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <span className={cn('text-sm font-semibold uppercase tracking-wide', iconColors[color])}>
            {title}
          </span>
          {icon && (
            <div className={cn('p-2 rounded-lg', iconBgColors[color], iconColors[color])}>
              {icon}
            </div>
          )}
        </div>
        
        <div className="text-gray-900 text-4xl md:text-5xl font-bold mb-3 tracking-tight">
          {value}
        </div>
        
        {subtitle && !change && (
          <div className="text-sm font-medium text-gray-600">
            {subtitle}
          </div>
        )}
        
        {change !== undefined && (
          <div className={cn(
            'flex items-center gap-1.5 text-sm font-semibold',
            change >= 0 ? 'text-green-600' : 'text-red-600'
          )}>
            {change >= 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span>{Math.abs(change)}% from last period</span>
          </div>
        )}
      </div>
    </div>
  );
};
