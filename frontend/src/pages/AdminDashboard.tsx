// Admin Dashboard - Created by Balaji Koneti
import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { dashboardService, UserData } from '../services/dashboardService';
import { LogOut, Users, BarChart3, AlertTriangle, CheckCircle } from 'lucide-react';

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [users, setUsers] = useState<UserData[]>([]);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    lowRisk: 0,
    highRisk: 0,
    criticalRisk: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [viewingAsUser, setViewingAsUser] = useState<UserData | null>(null);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Load admin dashboard data (includes users, predictions, and stats)
      const adminData = await dashboardService.getAdminDashboardData();
      
      console.log('Loaded users:', adminData.users.length);
      console.log('Loaded predictions:', adminData.predictions.length);
      console.log('Stats:', adminData.stats);
      
      setUsers(adminData.users);
      setPredictions(adminData.predictions);
      setStats(adminData.stats);
      setLoading(false);
      
    } catch (error) {
      console.error('Error loading admin data:', error);
      setError('Failed to load admin data');
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const getUserRiskLevel = (userId: string) => {
    const userPredictions = predictions.filter(p => p.userId === userId);
    if (userPredictions.length === 0) return 'unknown';
    
    // Get the most recent prediction
    const latestPrediction = userPredictions.sort((a, b) => 
      new Date(b.predictionDate).getTime() - new Date(a.predictionDate).getTime()
    )[0];
    
    return latestPrediction.riskLevel;
  };


  // const getRoleStats = () => {
  //   return users.reduce((acc, user) => {
  //     acc[user.role] = (acc[user.role] || 0) + 1;
  //     return acc;
  //   }, {} as Record<string, number>);
  // };

  const getDepartmentStats = () => {
    return users.reduce((acc, user) => {
      const dept = user.department || 'Unknown';
      acc[dept] = (acc[dept] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return <CheckCircle className="h-4 w-4" />;
      case 'medium': return <BarChart3 className="h-4 w-4" />;
      case 'high': return <AlertTriangle className="h-4 w-4" />;
      case 'critical': return <AlertTriangle className="h-4 w-4" />;
      default: return <BarChart3 className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadAdminData}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // const roleStats = getRoleStats();
  const departmentStats = getDepartmentStats();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-primary-600 mr-3" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Admin Dashboard
                </h1>
                <p className="text-sm text-gray-500">
                  Welcome back, {user?.firstName}! Manage your organization's burnout risk.
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {viewingAsUser && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Viewing as:</span>
                  <span className="text-sm font-medium text-blue-600">
                    {viewingAsUser.firstName} {viewingAsUser.lastName}
                  </span>
                  <button
                    onClick={() => setViewingAsUser(null)}
                    className="text-xs text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.totalUsers}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Low Risk</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.lowRisk}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">High Risk</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.highRisk}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Critical Risk</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.criticalRisk}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Level Distribution</h3>
            <div className="space-y-3">
              {Object.entries({
                low: stats.lowRisk,
                medium: Math.floor(stats.totalUsers * 0.2), // Estimate medium risk
                high: stats.highRisk,
                critical: stats.criticalRisk
              }).map(([level, count]) => (
                <div key={level} className="flex items-center justify-between">
                  <div className="flex items-center">
                    {getRiskIcon(level)}
                    <span className="ml-2 text-sm font-medium text-gray-700 capitalize">
                      {level} Risk
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          level === 'low' ? 'bg-green-500' :
                          level === 'medium' ? 'bg-yellow-500' :
                          level === 'high' ? 'bg-orange-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${(count / users.length) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-8">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Distribution</h3>
            <div className="space-y-3">
              {Object.entries(departmentStats).map(([dept, count]) => (
                <div key={dept} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">{dept}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${(count / users.length) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-8">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* User List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">All Users ({users.length})</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Job Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Work Patterns
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => {
                  const riskLevel = getUserRiskLevel(user._id);
                  return (
                    <tr 
                      key={user._id} 
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedUser(user)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                              <span className="text-sm font-medium text-gray-700">
                                {user.firstName[0]}{user.lastName[0]}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.firstName} {user.lastName}
                            </div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                          user.role === 'manager' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.department || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.jobTitle || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(riskLevel)}`}>
                          {getRiskIcon(riskLevel)}
                          <span className="ml-1 capitalize">{riskLevel}</span>
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.workPatterns ? (
                          <div className="text-xs">
                            <div>{user.workPatterns.workHoursPerWeek}h/week</div>
                            <div>{user.workPatterns.stressLevel}/10 stress</div>
                            {user.role === 'manager' && (
                              <div>{user.workPatterns.teamSize} team members</div>
                            )}
                          </div>
                        ) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setViewingAsUser(user);
                          }}
                          className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                        >
                          View As
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* User Detail Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {selectedUser.firstName} {selectedUser.lastName}
                  </h3>
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Email</label>
                    <p className="text-sm text-gray-900">{selectedUser.email}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Role</label>
                    <p className="text-sm text-gray-900 capitalize">{selectedUser.role}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Department</label>
                    <p className="text-sm text-gray-900">{selectedUser.department || 'N/A'}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Job Title</label>
                    <p className="text-sm text-gray-900">{selectedUser.jobTitle || 'N/A'}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Experience</label>
                    <p className="text-sm text-gray-900">{selectedUser.experienceYears || 0} years</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Current Risk Level</label>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(getUserRiskLevel(selectedUser._id))}`}>
                      {getRiskIcon(getUserRiskLevel(selectedUser._id))}
                      <span className="ml-1 capitalize">{getUserRiskLevel(selectedUser._id)}</span>
                    </span>
                  </div>
                  
                  {selectedUser.workPatterns && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Work Patterns</label>
                      <div className="text-xs text-gray-900 space-y-1">
                        <div>Work Hours: {selectedUser.workPatterns.workHoursPerWeek}/week</div>
                        <div>Stress Level: {selectedUser.workPatterns.stressLevel}/10</div>
                        <div>Work-Life Balance: {selectedUser.workPatterns.workLifeBalance}/10</div>
                        <div>Team Size: {selectedUser.workPatterns.teamSize || 'N/A'}</div>
                        <div>Remote Work: {selectedUser.workPatterns.remoteWorkPercentage}%</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;
