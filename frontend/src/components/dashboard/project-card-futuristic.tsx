import React from 'react';
import { cn } from '@/lib/utils';
import { StatusBadge } from '@/components/ui/status-badge';
import { Users, DollarSign, AlertTriangle } from 'lucide-react';

interface ProjectCardProps {
  project: {
    id: string;
    name: string;
    status?: string;
    progress?: number;
    budget?: number;
    risk_score?: number;
    team_size?: number;
  };
  onClick?: () => void;
}

export const ProjectCardFuturistic: React.FC<ProjectCardProps> = ({
  project,
  onClick,
}) => {
  const progress = project.progress || 0;
  const riskScore = project.risk_score || 0;
  const budget = project.budget || 0;
  const teamSize = project.team_size || 0;
  
  const riskLevel = riskScore > 70 ? 'error' : riskScore > 40 ? 'warning' : 'success';
  const statusMap: { [key: string]: 'success' | 'warning' | 'error' | 'info' } = {
    'Active': 'success',
    'active': 'success',
    'At Risk': 'warning',
    'at-risk': 'warning',
    'Completed': 'info',
    'completed': 'info',
    'On Hold': 'pending',
  };
  
  const statusBadge = statusMap[project.status || 'active'] || 'success';
  
  return (
    <div
      onClick={onClick}
      className={cn(
        'group relative rounded-2xl p-6 cursor-pointer',
        'bg-white backdrop-blur-xl',
        'border border-gray-200',
        'transition-all duration-500',
        'hover:border-cyan-400',
        'hover:shadow-lg hover:shadow-cyan-500/20',
        'hover:scale-[1.02]'
      )}
    >
      {/* Glow Effect on Hover */}
      <div className={cn(
        'absolute inset-0 rounded-2xl',
        'bg-gradient-to-br from-cyan-500/0 to-purple-500/0',
        'group-hover:from-cyan-500/5 group-hover:to-purple-500/5',
        'transition-all duration-500'
      )} />
      
      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 truncate flex-1 mr-2">
            {project.name}
          </h3>
          <StatusBadge
            status={statusBadge}
            label={project.status || 'Active'}
            size="sm"
          />
        </div>
        
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-600">Progress</span>
            <span className="text-gray-900 font-medium">{progress}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        
        {/* Meta Info */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <div className="min-w-0">
              <div className="text-gray-500 text-xs">Budget</div>
              <div className="text-gray-900 font-medium truncate">
                ${typeof budget === 'number' ? (budget / 1000).toFixed(0) : budget}K
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <AlertTriangle className={cn(
              'w-4 h-4 flex-shrink-0',
              riskLevel === 'error' ? 'text-red-500' :
              riskLevel === 'warning' ? 'text-yellow-500' :
              'text-green-500'
            )} />
            <div className="min-w-0">
              <div className="text-gray-500 text-xs">Risk</div>
              <div className={cn(
                'font-medium truncate',
                riskLevel === 'error' ? 'text-red-500' :
                riskLevel === 'warning' ? 'text-yellow-500' :
                'text-green-500'
              )}>
                {riskScore}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-gray-500 flex-shrink-0" />
            <div className="min-w-0">
              <div className="text-gray-500 text-xs">Team</div>
              <div className="text-gray-900 font-medium truncate">{teamSize}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
