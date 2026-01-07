import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Shield, Activity, Ban, AlertTriangle, RefreshCw } from 'lucide-react';
import { Link } from "react-router-dom";

const API_BASE = '/api/dashboard';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [trafficData, setTrafficData] = useState([]);
  const [suspiciousIPs, setSuspiciousIPs] = useState([]);
  const [blockedIPs, setBlockedIPs] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('suspicious');

  // Fill missing hours with 0 requests
  const processTrafficData = (data) => {
    if (!data || data.length === 0) {
      const result = [];
      for (let i = 23; i >= 0; i--) {
        const hour = new Date();
        hour.setHours(hour.getHours() - i);
        result.push({
          time: hour.getHours().toString().padStart(2, '0') + ':00',
          requests: 0
        });
      }
      return result;
    }

    const dataMap = {};
    data.forEach(item => {
      dataMap[item.time] = item.requests;
    });

    const result = [];
    for (let i = 23; i >= 0; i--) {
      const hour = new Date();
      hour.setHours(hour.getHours() - i);
      const hourStr = hour.getHours().toString().padStart(2, '0') + ':00';
      result.push({
        time: hourStr,
        requests: dataMap[hourStr] || 0
      });
    }

    return result;
  };

  // Fetch all data
  const fetchData = async () => {
    try {
      const [statsRes, trafficRes, suspiciousRes, blockedRes, activityRes] = await Promise.all([
        fetch(`${API_BASE}/stats`),
        fetch(`${API_BASE}/traffic-chart`),
        fetch(`${API_BASE}/suspicious-ips`),
        fetch(`${API_BASE}/blocked-ips`),
        fetch(`${API_BASE}/recent-activity`)
      ]);

      setStats(await statsRes.json());
      
      const rawTrafficData = await trafficRes.json();
      const processedTraffic = processTrafficData(rawTrafficData);
      setTrafficData(processedTraffic);
      
      setSuspiciousIPs((await suspiciousRes.json()).data || []);
      setBlockedIPs((await blockedRes.json()).data || []);
      setRecentActivity(await activityRes.json());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleBlock = async (ip) => {
    try {
      await fetch(`${API_BASE}/block-ip/${ip}`, { method: 'POST' });
      fetchData();
    } catch (error) {
      console.error('Error blocking IP:', error);
    }
  };

  const handleUnblock = async (ip) => {
    try {
      await fetch(`${API_BASE}/unblock-ip/${ip}`, { method: 'POST' });
      fetchData();
    } catch (error) {
      console.error('Error unblocking IP:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4" style={{color: '#00ffaa'}} />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <style>
        {`
          .text-gradient {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }
          .btn-gradient {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
          }
          .card-gradient {
            background: linear-gradient(135deg, rgba(0, 255, 170, 0.05) 0%, rgba(0, 204, 255, 0.05) 100%);
          }
          .border-gradient {
            border-color: rgba(0, 255, 170, 0.2);
          }
        `}
      </style>

      <header className="bg-black bg-opacity-95 backdrop-blur-lg shadow-lg border-b border-gradient">
        <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8" style={{color: '#00ffaa'}} />
              <h1 className="text-3xl font-bold text-gradient">CWatch Protection Dashboard</h1>
            </div>
            <button
              onClick={fetchData}
              className="flex items-center space-x-2 px-6 py-3 btn-gradient text-black rounded-full hover:scale-105 transition-all duration-300 font-bold shadow-lg"
              style={{boxShadow: '0 10px 30px rgba(0, 255, 170, 0.3)'}}
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <Link
              to="/dashboard/settings"
              className="btn-gradient text-black px-8 py-3 text-base font-bold rounded-full transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-cyan-500/40 inline-block text-center"
              >
              Settings
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Requests"
            value={stats?.total_requests || 0}
            subtitle={`${stats?.requests_today || 0} today`}
            icon={<Activity className="w-6 h-6" style={{color: '#00ccff'}} />}
          />
          <StatCard
            title="Requests/Second"
            value={stats?.requests_per_second || 0}
            subtitle={`${stats?.requests_hour || 0} last hour`}
            icon={<Activity className="w-6 h-6" style={{color: '#00ffaa'}} />}
          />
          <StatCard
            title="Suspicious IPs"
            value={stats?.suspicious_ips || 0}
            subtitle="Need attention"
            icon={<AlertTriangle className="w-6 h-6" style={{color: '#ffaa00'}} />}
          />
          <StatCard
            title="Blocked IPs"
            value={stats?.blocked_ips || 0}
            subtitle="Currently blocked"
            icon={<Ban className="w-6 h-6" style={{color: '#ff4444'}} />}
          />
        </div>

        <div className="card-gradient rounded-3xl border border-gradient p-8 mb-8 shadow-xl">
          <h2 className="text-2xl font-bold text-gradient mb-6">Traffic (Last 24 Hours)</h2>
          {trafficData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trafficData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  dataKey="time" 
                  stroke="#a0a0a0"
                  tick={{ fontSize: 12, fill: '#a0a0a0' }}
                />
                <YAxis 
                  stroke="#a0a0a0"
                  tick={{ fontSize: 12, fill: '#a0a0a0' }}
                  allowDecimals={false}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1a1a1a',
                    border: '1px solid rgba(0, 255, 170, 0.3)',
                    borderRadius: '12px',
                    color: '#ffffff'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="requests" 
                  stroke="#00ffaa" 
                  strokeWidth={3}
                  dot={{ fill: '#00ffaa', r: 4 }}
                  activeDot={{ r: 6, fill: '#00ccff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-500">
              No traffic data available
            </div>
          )}
        </div>

        <div className="card-gradient rounded-3xl border border-gradient shadow-xl overflow-hidden">
          <div className="border-b border-gradient">
            <nav className="flex space-x-8 px-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('suspicious')}
                className={`py-5 px-1 border-b-2 font-medium text-sm transition-all duration-300 ${
                  activeTab === 'suspicious'
                    ? 'border-cyan-400 text-gradient'
                    : 'border-transparent text-gray-500 hover:text-gray-300'
                }`}
              >
                Suspicious IPs ({suspiciousIPs.length})
              </button>
              <button
                onClick={() => setActiveTab('blocked')}
                className={`py-5 px-1 border-b-2 font-medium text-sm transition-all duration-300 ${
                  activeTab === 'blocked'
                    ? 'border-cyan-400 text-gradient'
                    : 'border-transparent text-gray-500 hover:text-gray-300'
                }`}
              >
                Blocked IPs ({blockedIPs.length})
              </button>
              <button
                onClick={() => setActiveTab('activity')}
                className={`py-5 px-1 border-b-2 font-medium text-sm transition-all duration-300 ${
                  activeTab === 'activity'
                    ? 'border-cyan-400 text-gradient'
                    : 'border-transparent text-gray-500 hover:text-gray-300'
                }`}
              >
                Recent Activity
              </button>
            </nav>
          </div>

          <div className="p-8">
            {activeTab === 'suspicious' && (
              <IPTable
                ips={suspiciousIPs}
                type="suspicious"
                onBlock={handleBlock}
              />
            )}
            {activeTab === 'blocked' && (
              <IPTable
                ips={blockedIPs}
                type="blocked"
                onUnblock={handleUnblock}
              />
            )}
            {activeTab === 'activity' && (
              <ActivityList activities={recentActivity} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon }) {
  return (
    <div className="card-gradient rounded-3xl border border-gradient p-6 transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:shadow-cyan-500/20 hover:border-cyan-400/50 cursor-pointer">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 rounded-xl" style={{background: 'rgba(0, 255, 170, 0.1)'}}>
          {icon}
        </div>
      </div>
      <h3 className="text-3xl font-bold text-white mb-2">{value}</h3>
      <p className="text-sm font-medium text-gray-400 mb-1">{title}</p>
      <p className="text-xs text-gray-500">{subtitle}</p>
    </div>
  );
}

function IPTable({ ips, type, onBlock, onUnblock }) {
  if (ips.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No {type} IPs found</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead>
          <tr className="border-b border-gradient">
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">
              IP Address
            </th>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">
              Reason
            </th>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">
              Time
            </th>
            <th className="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">
              Action
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {ips.map((ip) => (
            <tr key={ip.id} className="hover:bg-black hover:bg-opacity-30 transition-colors duration-200">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                {ip.ip}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                {ip.reason}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                {new Date(ip.detected_at || ip.blocked_at).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {type === 'suspicious' ? (
                  <button
                    onClick={() => onBlock(ip.ip)}
                    className="px-5 py-2 bg-red-600 text-white text-xs font-bold rounded-full hover:bg-red-700 hover:scale-105 transition-all duration-300 shadow-lg"
                  >
                    Block
                  </button>
                ) : (
                  <button
                    onClick={() => onUnblock(ip.ip)}
                    className="px-5 py-2 text-black text-xs font-bold rounded-full hover:scale-105 transition-all duration-300 shadow-lg btn-gradient"
                  >
                    Unblock
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ActivityList({ activities }) {
  if (activities.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No recent activity</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <div key={index} className="flex items-start space-x-4 p-5 rounded-2xl border border-gradient hover:border-cyan-400/50 transition-all duration-300" style={{background: 'rgba(0, 0, 0, 0.3)'}}>
          <div className={`p-3 rounded-full ${
            activity.status === 'blocked' ? 'bg-red-900 bg-opacity-30' : 'bg-yellow-900 bg-opacity-30'
          }`}>
            {activity.status === 'blocked' ? (
              <Ban className="w-5 h-5 text-red-500" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
            )}
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-white">{activity.ip}</p>
            <p className="text-sm text-gray-400 mt-1">{activity.reason}</p>
            <p className="text-xs text-gray-500 mt-2">
              {new Date(activity.time).toLocaleString()}
            </p>
          </div>
          <span className={`px-3 py-1 text-xs font-bold rounded-full ${
            activity.status === 'blocked'
              ? 'bg-red-900 bg-opacity-40 text-red-300'
              : activity.status === 'verified'
              ? 'bg-green-900 bg-opacity-40 text-green-300'
              : 'bg-yellow-900 bg-opacity-40 text-yellow-300'
          }`}>
            {activity.status}
          </span>
        </div>
      ))}
    </div>
  );
}