import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Shield, Activity, Ban, AlertTriangle, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api/dashboard';

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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin text-orange-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-orange-500" />
              <h1 className="text-2xl font-bold text-gray-900">CWatch Protection Dashboard</h1>
            </div>
            <button
              onClick={fetchData}
              className="flex items-center space-x-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Requests"
            value={stats?.total_requests || 0}
            subtitle={`${stats?.requests_today || 0} today`}
            icon={<Activity className="w-6 h-6 text-blue-500" />}
            color="blue"
          />
          <StatCard
            title="Requests/Second"
            value={stats?.requests_per_second || 0}
            subtitle={`${stats?.requests_hour || 0} last hour`}
            icon={<Activity className="w-6 h-6 text-green-500" />}
            color="green"
          />
          <StatCard
            title="Suspicious IPs"
            value={stats?.suspicious_ips || 0}
            subtitle="Need attention"
            icon={<AlertTriangle className="w-6 h-6 text-yellow-500" />}
            color="yellow"
          />
          <StatCard
            title="Blocked IPs"
            value={stats?.blocked_ips || 0}
            subtitle="Currently blocked"
            icon={<Ban className="w-6 h-6 text-red-500" />}
            color="red"
          />
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Traffic (Last 24 Hours)</h2>
          {trafficData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trafficData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="time" 
                  stroke="#6b7280"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  stroke="#6b7280"
                  tick={{ fontSize: 12 }}
                  allowDecimals={false}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="requests" 
                  stroke="#f97316" 
                  strokeWidth={2}
                  dot={{ fill: '#f97316', r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-500">
              No traffic data available
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-sm">
          <div className="border-b">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('suspicious')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                  activeTab === 'suspicious'
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Suspicious IPs ({suspiciousIPs.length})
              </button>
              <button
                onClick={() => setActiveTab('blocked')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                  activeTab === 'blocked'
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Blocked IPs ({blockedIPs.length})
              </button>
              <button
                onClick={() => setActiveTab('activity')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                  activeTab === 'activity'
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Recent Activity
              </button>
            </nav>
          </div>

          <div className="p-6">
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

function StatCard({ title, value, subtitle, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    yellow: 'bg-yellow-50',
    red: 'bg-red-50'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
      <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
      <p className="text-sm font-medium text-gray-600 mt-1">{title}</p>
      <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
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
      <table className="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              IP Address
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Reason
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Time
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Action
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {ips.map((ip) => (
            <tr key={ip.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {ip.ip}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {ip.reason}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(ip.detected_at || ip.blocked_at).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {type === 'suspicious' ? (
                  <button
                    onClick={() => onBlock(ip.ip)}
                    className="px-4 py-2 bg-red-500 text-white text-xs font-medium rounded hover:bg-red-600 transition"
                  >
                    Block
                  </button>
                ) : (
                  <button
                    onClick={() => onUnblock(ip.ip)}
                    className="px-4 py-2 bg-green-500 text-white text-xs font-medium rounded hover:bg-green-600 transition"
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
        <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
          <div className={`p-2 rounded-full ${
            activity.status === 'blocked' ? 'bg-red-100' : 'bg-yellow-100'
          }`}>
            {activity.status === 'blocked' ? (
              <Ban className="w-4 h-4 text-red-600" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-yellow-600" />
            )}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">{activity.ip}</p>
            <p className="text-sm text-gray-600">{activity.reason}</p>
            <p className="text-xs text-gray-500 mt-1">
              {new Date(activity.time).toLocaleString()}
            </p>
          </div>
          <span className={`px-2 py-1 text-xs font-medium rounded ${
            activity.status === 'blocked'
              ? 'bg-red-100 text-red-800'
              : activity.status === 'verified'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {activity.status}
          </span>
        </div>
      ))}
    </div>
  );
}