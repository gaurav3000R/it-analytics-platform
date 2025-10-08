"use client";

import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, Users, Activity, Clock, DollarSign, CheckCircle, XCircle } from 'lucide-react';

const API_URL = 'http://localhost:8000/api/v1';

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [riskDashboard, setRiskDashboard] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [overviewRes, riskRes, projectsRes] = await Promise.all([
        fetch(`${API_URL}/analytics/overview`),
        fetch(`${API_URL}/risks/dashboard`),
        fetch(`${API_URL}/projects/`)
      ]);

      if (!overviewRes.ok || !riskRes.ok || !projectsRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const overviewData = await overviewRes.json();
      const riskData = await riskRes.json();
      const projectsData = await projectsRes.json();

      setOverview(overviewData);
      setRiskDashboard(riskData);
      setProjects(projectsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score) => {
    if (score >= 70) return 'text-red-500 bg-red-50';
    if (score >= 40) return 'text-yellow-500 bg-yellow-50';
    return 'text-green-500 bg-green-50';
  };

  const getRiskBadge = (score) => {
    if (score >= 70) return { label: 'High Risk', color: 'bg-red-500' };
    if (score >= 40) return { label: 'Medium Risk', color: 'bg-yellow-500' };
    return { label: 'Low Risk', color: 'bg-green-500' };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Error Loading Data</h2>
          <p className="text-gray-300">{error}</p>
          <button 
            onClick={fetchData}
            className="mt-4 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          Operational Risk Early Warning System
        </h1>
        <p className="text-gray-300">AI-Powered IT Services Project Analytics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Activity className="w-8 h-8" />}
          title="Active Projects"
          value={overview?.total_projects || 0}
          change="+12%"
          positive={true}
        />
        <StatCard
          icon={<Users className="w-8 h-8" />}
          title="Team Members"
          value={overview?.total_employees || 0}
          change="+5%"
          positive={true}
        />
        <StatCard
          icon={<AlertTriangle className="w-8 h-8" />}
          title="High Risk Projects"
          value={riskDashboard?.high_risk_count || 0}
          change="-3%"
          positive={true}
        />
        <StatCard
          icon={<TrendingUp className="w-8 h-8" />}
          title="Avg Risk Score"
          value={riskDashboard?.average_risk_score?.toFixed(1) || 0}
          change="-8%"
          positive={true}
        />
      </div>

      {/* Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
          <h3 className="text-white text-xl font-bold mb-4">Risk Distribution</h3>
          <div className="space-y-4">
            <RiskBar label="High Risk" count={riskDashboard?.high_risk_count || 0} color="bg-red-500" />
            <RiskBar label="Medium Risk" count={riskDashboard?.medium_risk_count || 0} color="bg-yellow-500" />
            <RiskBar label="Low Risk" count={riskDashboard?.low_risk_count || 0} color="bg-green-500" />
          </div>
        </div>

        <div className="lg:col-span-2 bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
          <h3 className="text-white text-xl font-bold mb-4">System Status</h3>
          <div className="grid grid-cols-2 gap-4">
            <StatusItem icon={<CheckCircle />} label="Anomaly Detection" status="Active" color="text-green-400" />
            <StatusItem icon={<CheckCircle />} label="Risk Prediction" status="Active" color="text-green-400" />
            <StatusItem icon={<Clock />} label="Last Sync" status="2 min ago" color="text-blue-400" />
            <StatusItem icon={<Activity />} label="Data Quality" status="98%" color="text-green-400" />
          </div>
        </div>
      </div>

      {/* Projects Table */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-white text-xl font-bold">Project Risk Overview</h3>
          <button 
            onClick={fetchData}
            className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <Activity className="w-4 h-4" />
            Refresh
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/20">
                <th className="text-left py-3 px-4 text-gray-300 font-semibold">Project</th>
                <th className="text-left py-3 px-4 text-gray-300 font-semibold">Manager</th>
                <th className="text-center py-3 px-4 text-gray-300 font-semibold">Team Size</th>
                <th className="text-center py-3 px-4 text-gray-300 font-semibold">Budget</th>
                <th className="text-center py-3 px-4 text-gray-300 font-semibold">Status</th>
                <th className="text-center py-3 px-4 text-gray-300 font-semibold">Risk Score</th>
              </tr>
            </thead>
            <tbody>
              {projects.slice(0, 10).map((project) => {
                const badge = getRiskBadge(project.risk_score || 0);
                return (
                  <tr key={project.id} className="border-b border-white/10 hover:bg-white/5 transition-colors">
                    <td className="py-4 px-4">
                      <div className="text-white font-medium">{project.name}</div>
                      <div className="text-gray-400 text-sm">{project.description?.slice(0, 50)}...</div>
                    </td>
                    <td className="py-4 px-4 text-gray-300">{project.project_manager}</td>
                    <td className="py-4 px-4 text-center">
                      <span className="text-white font-medium">{project.team_size}</span>
                    </td>
                    <td className="py-4 px-4 text-center text-gray-300">
                      ${(project.budget || 0).toLocaleString()}
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        project.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {project.status}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${badge.color} text-white`}>
                          {(project.risk_score || 0).toFixed(0)}
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, change, positive }) {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 bg-purple-500/20 rounded-xl text-purple-400">
          {icon}
        </div>
        <span className={`text-sm font-medium ${positive ? 'text-green-400' : 'text-red-400'}`}>
          {change}
        </span>
      </div>
      <h3 className="text-gray-300 text-sm mb-1">{title}</h3>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  );
}

function RiskBar({ label, count, color }) {
  const maxCount = 20;
  const percentage = (count / maxCount) * 100;
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-gray-300">{label}</span>
        <span className="text-white font-medium">{count}</span>
      </div>
      <div className="w-full bg-white/10 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all duration-500`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}

function StatusItem({ icon, label, status, color }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
      <div className={color}>{icon}</div>
      <div>
        <div className="text-gray-400 text-xs">{label}</div>
        <div className="text-white text-sm font-medium">{status}</div>
      </div>
    </div>
  );
}