import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, TrendingDown, Trophy, Target, AlertCircle, CheckCircle2, Brain, Clock, Zap } from 'lucide-react';
import api from '@/services/api';
import { User, Analysis, MoveQualityStats } from '@/types';
import toast from 'react-hot-toast';

const MoveQualityChart: React.FC<{ data: MoveQualityStats }> = ({ data }) => {
  const chartData = [
    { name: 'Brilliant', value: data.brilliant_moves, fill: '#10b981' },
    { name: 'Great', value: data.great_moves, fill: '#22c55e' },
    { name: 'Best', value: data.best_moves, fill: '#84cc16' },
    { name: 'Excellent', value: data.excellent_moves, fill: '#eab308' },
    { name: 'Good', value: data.good_moves, fill: '#f59e0b' },
    { name: 'Inaccuracy', value: data.inaccuracies, fill: '#f97316' },
    { name: 'Mistake', value: data.mistakes, fill: '#ef4444' },
    { name: 'Blunder', value: data.blunders, fill: '#dc2626' },
  ].filter(item => item.value > 0);

  return (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
      <h3 className="text-lg font-semibold mb-4 text-white">Move Quality Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#374151', border: 'none', borderRadius: '8px', color: '#fff' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

const PerformanceCard: React.FC<{
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  subtitle?: string;
}> = ({ title, value, change, icon, trend, subtitle }) => {
  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-400" />;
    if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-400" />;
    return null;
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
          {change !== undefined && (
            <div className="flex items-center mt-2">
              {getTrendIcon()}
              <span className={`text-sm ml-1 ${
                trend === 'up' ? 'text-green-400' : 
                trend === 'down' ? 'text-red-400' : 
                'text-gray-400'
              }`}>
                {change > 0 ? '+' : ''}{change} from last week
              </span>
            </div>
          )}
        </div>
        <div className="text-blue-400">{icon}</div>
      </div>
    </div>
  );
};

const CoachingInsightCard: React.FC<{
  category: string;
  priority: 'high' | 'medium' | 'low';
  description: string;
  improvement: string;
}> = ({ category, priority, description, improvement }) => {
  const getPriorityColor = () => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-900/20 border-red-800';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20 border-yellow-800';
      case 'low': return 'text-green-400 bg-green-900/20 border-green-800';
    }
  };

  const getPriorityIcon = () => {
    switch (priority) {
      case 'high': return <AlertCircle className="w-5 h-5" />;
      case 'medium': return <Target className="w-5 h-5" />;
      case 'low': return <CheckCircle2 className="w-5 h-5" />;
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${getPriorityColor()}`}>
      <div className="flex items-start space-x-3">
        {getPriorityIcon()}
        <div className="flex-1">
          <h4 className="font-semibold capitalize text-white">{category.replace('_', ' ')}</h4>
          <p className="text-sm mt-1 text-gray-300">{description}</p>
          <p className="text-xs mt-2 font-medium">💡 {improvement}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          priority === 'high' ? 'bg-red-800 text-red-200' :
          priority === 'medium' ? 'bg-yellow-800 text-yellow-200' :
          'bg-green-800 text-green-200'
        }`}>
          {priority.toUpperCase()}
        </span>
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const router = useRouter();
  const { username } = router.query;
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch user data by username
  const { data: userData, error: userError, isLoading: userLoading } = useQuery({
    queryKey: ['user', username],
    queryFn: () => api.users.getByUsername(username as string),
    enabled: !!username,
  });

  // Fetch analysis summary
  const { data: analysisSummary, isLoading: summaryLoading } = useQuery({
    queryKey: ['analysis-summary', user?.id],
    queryFn: () => api.analysis.getSummary(user!.id, 7),
    enabled: !!user?.id,
  });

  // Fetch recommendations
  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', user?.id],
    queryFn: () => api.insights.getRecommendations(user!.id),
    enabled: !!user?.id,
  });

  useEffect(() => {
    // Handle missing username - redirect to home
    if (!router.isReady) return;
    
    if (!username) {
      toast.error('No username provided. Redirecting to home...');
      router.push('/');
      return;
    }
    
    // Handle user data loading states
    if (userData) {
      setUser(userData);
      setLoading(false);
    } else if (userError) {
      toast.error('Failed to load user data');
      setLoading(false);
      router.push('/');
    } else if (!userLoading && !userData) {
      // Query is enabled but no data and not loading = user not found
      setLoading(false);
    }
  }, [userData, userError, userLoading, username, router]);

  const [isFetching, setIsFetching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFetchGames = async () => {
    if (!user) return;
    setIsFetching(true);
    try {
      const result = await api.games.fetchRecent(user.id, 7);
      if (result.games_added === 0) {
        toast('No new games found', { icon: 'ℹ️' });
      } else {
        toast.success(`🎉 Fetched ${result.games_added} new games from Chess.com!`);
      }
    } catch (error: any) {
      console.error('Error fetching games:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch games from Chess.com';
      toast.error(`❌ ${errorMessage}`);
    } finally {
      setIsFetching(false);
    }
  };

  const handleAnalyzeGames = async (forceReanalysis = false) => {
    if (!user) return;
    setIsAnalyzing(true);
    try {
      const result = await api.analysis.analyzeGames(user.id, { 
        days: 7,
        forceReanalysis 
      });
      if (result.games_queued === 0) {
        // Check if games exist but are already analyzed
        if (userData?.total_games && userData.total_games > 0) {
          toast('✅ All games already analyzed! Sync new games to analyze more.', { 
            icon: '✅',
            duration: 4000 
          });
        } else {
          toast('No games to analyze. Sync games from Chess.com first!', { 
            icon: '🤔' 
          });
        }
      } else {
        const message = forceReanalysis 
          ? `🔄 Re-analyzing ${result.games_queued} games with fresh analysis!`
          : `🧠 Started AI analysis for ${result.games_queued} games!`;
        toast.success(message);
      }
    } catch (error: any) {
      console.error('Error analyzing games:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to start analysis';
      toast.error(`❌ ${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Use real recommendations from API or show placeholder message
  const coachingInsights = recommendations || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading your chess insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <div className="text-4xl">♔</div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-white">
                Welcome back, {user?.display_name || user?.chesscom_username}!
              </h1>
            </div>
            {/* Connection Status Indicator */}
            <div className="flex items-center space-x-2 bg-gray-800 px-4 py-2 rounded-lg border border-gray-700">
              <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
              <span className="text-sm text-gray-300">
                {userData?.connection_status || 'Public Data Only'}
              </span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-gray-300">
              Your chess performance insights and coaching recommendations
            </p>
            {userData && !userData.can_access_private_data && (
              <div className="text-xs text-gray-500 bg-gray-800 px-3 py-1 rounded-full border border-gray-700">
                🔍 Using public Chess.com data
              </div>
            )}
          </div>
        </div>

        {/* Games Summary */}
        {userData && (
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Total Games Fetched</p>
                <p className="text-2xl font-bold text-white">{userData.total_games || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Games Analyzed</p>
                <p className="text-2xl font-bold text-white">{analysisSummary?.total_games_analyzed || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Status</p>
                <p className="text-sm font-medium text-yellow-400">
                  {analysisSummary?.total_games_analyzed === 0 ? 'Ready for Analysis' : 'Analyzed'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button
            onClick={handleFetchGames}
            disabled={isFetching}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center space-x-2"
          >
            {isFetching ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            ) : (
              <Clock className="w-4 h-4" />
            )}
            <span>{isFetching ? 'Syncing...' : 'Sync Recent Games'}</span>
          </button>
          <button
            onClick={() => handleAnalyzeGames(false)}
            disabled={isAnalyzing}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center space-x-2"
          >
            {isAnalyzing ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            ) : (
              <Brain className="w-4 h-4" />
            )}
            <span>{isAnalyzing ? 'Analyzing...' : 'Analyze with AI'}</span>
          </button>
          
          {/* Force Reanalyze button - only show if games are analyzed */}
          {analysisSummary && analysisSummary.total_games_analyzed > 0 && (
            <button
              onClick={() => handleAnalyzeGames(true)}
              disabled={isAnalyzing}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center space-x-2"
              title="Re-analyze all games (ignores previous analysis)"
            >
              {isAnalyzing ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              ) : (
                <Brain className="w-4 h-4" />
              )}
              <span>Force Re-analyze</span>
            </button>
          )}
          
          {/* Future OAuth Upgrade Button */}
          {userData && userData.connection_type === 'username_only' && (
            <button
              disabled
              className="bg-gray-700 text-gray-400 px-6 py-3 rounded-lg cursor-not-allowed font-medium flex items-center space-x-2 border border-gray-600"
              title="OAuth integration coming soon when Chess.com provides API access"
            >
              <div className="text-sm">🔐</div>
              <span>Upgrade to OAuth</span>
              <div className="text-xs bg-gray-600 px-2 py-1 rounded">
                Future
              </div>
            </button>
          )}
        </div>

        {/* Performance Overview Cards */}
        {analysisSummary && !summaryLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <PerformanceCard
              title="Games Analyzed"
              value={analysisSummary.total_games_analyzed}
              icon={<Trophy className="w-6 h-6" />}
              subtitle="Last 7 days"
            />
            <PerformanceCard
              title="Average Accuracy"
              value={`${analysisSummary.accuracy_percentage?.toFixed(1) || 0}%`}
              change={5.2}
              trend="up"
              icon={<Target className="w-6 h-6" />}
              subtitle="Higher is better"
            />
            <PerformanceCard
              title="ACPL"
              value={analysisSummary.average_acpl?.toFixed(0) || 'N/A'}
              change={-8}
              trend="up"
              icon={<Brain className="w-6 h-6" />}
              subtitle="Lower is better"
            />
            <PerformanceCard
              title="Favorite Opening"
              value={analysisSummary.most_played_openings?.[0]?.[0]?.substring(0, 15) + '...' || 'N/A'}
              icon={<Zap className="w-6 h-6" />}
              subtitle="Most played this week"
            />
          </div>
        )}

        {/* Charts and Insights Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Move Quality Chart */}
          {analysisSummary?.move_quality_breakdown && (
            <MoveQualityChart data={analysisSummary.move_quality_breakdown} />
          )}
          
          {/* Phase Performance */}
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-white">Phase Performance (ACPL)</h3>
            {analysisSummary?.phase_performance ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={[
                    { phase: 'Opening', acpl: analysisSummary.phase_performance.opening_acpl || 25 },
                    { phase: 'Middlegame', acpl: analysisSummary.phase_performance.middlegame_acpl || 35 },
                    { phase: 'Endgame', acpl: analysisSummary.phase_performance.endgame_acpl || 20 },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="phase" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#374151', 
                      border: 'none', 
                      borderRadius: '8px', 
                      color: '#fff' 
                    }} 
                  />
                  <Bar dataKey="acpl" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                <div className="text-center">
                  <Trophy className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                  <p>No phase data available yet</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Coaching Insights */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-8">
          <div className="flex items-center space-x-2 mb-6">
            <Brain className="w-6 h-6 text-blue-400" />
            <h3 className="text-xl font-semibold text-white">AI Coach Insights</h3>
          </div>
          <div className="space-y-4">
            {coachingInsights.length > 0 ? (
              coachingInsights.map((insight, index) => (
                <CoachingInsightCard
                  key={index}
                  category={insight.category}
                  priority={insight.priority}
                  description={insight.description}
                  improvement={insight.improvement}
                />
              ))
            ) : (
              <div className="flex items-center justify-center py-12 text-gray-500">
                <div className="text-center">
                  <Brain className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                  <p className="text-lg font-medium text-gray-400 mb-2">No insights available yet</p>
                  <p className="text-sm text-gray-500 max-w-md mx-auto">
                    Click <strong>"Analyze with AI"</strong> above to analyze your games and generate personalized coaching insights.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* No Data State */}
        {(!analysisSummary || analysisSummary.total_games_analyzed === 0) && !summaryLoading && (
          <div className="text-center py-12 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-gray-500 mb-4">
              <Trophy className="w-16 h-16 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Ready to start your chess journey?
            </h3>
            <p className="text-gray-400 mb-6 max-w-md mx-auto">
              Connect your Chess.com account and let our AI analyze your games to provide personalized coaching insights.
            </p>
            <div className="space-x-4">
              <button
                onClick={handleFetchGames}
                disabled={isFetching}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center space-x-2 mx-auto"
              >
                {isFetching ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Clock className="w-4 h-4" />
                )}
                <span>{isFetching ? 'Syncing Games...' : 'Sync Your Games'}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
