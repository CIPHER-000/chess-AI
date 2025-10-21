import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/router';
import api from '@/services/api';
import toast from 'react-hot-toast';
import { User, UserCreate } from '@/types';

interface LoginFormData {
  chesscom_username: string;
  email?: string;
}

const HomePage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [pollingStatus, setPollingStatus] = useState<string>('');
  const router = useRouter();
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>();

  /**
   * Poll user data until games are fetched
   * @param username Chess.com username
   * @param userId User ID
   * @param maxAttempts Maximum polling attempts (default: 10)
   * @param intervalMs Polling interval in milliseconds (default: 3000)
   */
  const pollUserData = async (
    username: string, 
    userId: number,
    maxAttempts = 10,
    intervalMs = 3000
  ): Promise<void> => {
    let attempts = 0;
    
    const checkUserData = async (): Promise<boolean> => {
      try {
        attempts++;
        setPollingStatus(`Fetching your games... (${attempts}/${maxAttempts})`);
        
        const userData = await api.users.getByUsername(username);
        
        // Check if games have been fetched (total_games > 0)
        if (userData.total_games && userData.total_games > 0) {
          toast.success(`✅ Fetched ${userData.total_games} games! Redirecting...`);
          setUser(userData);
          router.push(`/dashboard?userId=${userId}`);
          return true;
        }
        
        // Continue polling if games not yet fetched
        if (attempts >= maxAttempts) {
          toast('⏱️ Still fetching games in background. Redirecting to dashboard...', { 
            duration: 4000 
          });
          router.push(`/dashboard?userId=${userId}`);
          return true;
        }
        
        return false;
      } catch (error) {
        console.error('Polling error:', error);
        return false;
      }
    };
    
    // Initial check
    const immediate = await checkUserData();
    if (immediate) return;
    
    // Set up polling interval
    const pollInterval = setInterval(async () => {
      const shouldStop = await checkUserData();
      if (shouldStop) {
        clearInterval(pollInterval);
        setLoading(false);
        setPollingStatus('');
      }
    }, intervalMs);
    
    // Timeout after max attempts
    setTimeout(() => {
      clearInterval(pollInterval);
      setLoading(false);
      setPollingStatus('');
    }, maxAttempts * intervalMs + 1000);
  };

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setPollingStatus('');
    
    try {
      // Try to find existing user first
      try {
        const existingUser = await api.users.getByUsername(data.chesscom_username);
        
        if (existingUser.total_games && existingUser.total_games > 0) {
          // User exists and has games
          setUser(existingUser);
          toast.success('Welcome back!');
          router.push(`/dashboard?userId=${existingUser.id}`);
          setLoading(false);
        } else {
          // User exists but no games yet - start polling
          toast('Fetching your games...', { icon: '⏳' });
          await pollUserData(data.chesscom_username, existingUser.id);
        }
      } catch (error) {
        // User doesn't exist, create new one
        setPollingStatus('Creating account...');
        const newUser = await api.users.create({
          chesscom_username: data.chesscom_username,
          email: data.email
        });
        
        setUser(newUser);
        toast.success('Account created! Fetching your games...', { icon: '🎉' });
        
        // Start polling for game data
        await pollUserData(data.chesscom_username, newUser.id);
      }
    } catch (error: any) {
      console.error('Submit error:', error);
      toast.error(error.response?.data?.detail || 'Failed to login/create account');
      setLoading(false);
      setPollingStatus('');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">♔</div>
          <h1 className="text-3xl font-bold text-white mb-2">Chess Insight AI</h1>
          <p className="text-gray-300">
            Analyze your Chess.com games and improve your play with AI-powered insights.
          </p>
        </div>

        {/* Connection Form */}
        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-8">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-white mb-2">Get Started</h2>
            <p className="text-gray-400 text-sm">
              Enter your Chess.com username to access public game data and analysis
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="chesscom_username" className="block text-sm font-medium text-gray-200 mb-2">
                Chess.com Username
              </label>
              <input
                id="chesscom_username"
                type="text"
                {...register('chesscom_username', { 
                  required: 'Chess.com username is required',
                  minLength: {
                    value: 3,
                    message: 'Username must be at least 3 characters'
                  }
                })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your Chess.com username"
              />
              {errors.chesscom_username && (
                <p className="mt-1 text-sm text-red-400">{errors.chesscom_username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-200 mb-2">
                Email (Optional)
              </label>
              <input
                id="email"
                type="email"
                {...register('email')}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="your@email.com"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {pollingStatus || 'Connecting...'}
                </span>
              ) : 'Get Started'}
            </button>

            {pollingStatus && (
              <div className="mt-4 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
                <div className="flex items-center text-blue-400">
                  <svg className="animate-spin h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <div>
                    <p className="font-medium">{pollingStatus}</p>
                    <p className="text-sm text-blue-300 mt-1">Please wait while we fetch your recent games from Chess.com...</p>
                  </div>
                </div>
              </div>
            )}
          </form>

          {/* OAuth Connection Section */}
          <div className="mt-8 pt-6 border-t border-gray-700">
            <div className="text-center mb-4">
              <h3 className="text-sm font-medium text-gray-300 mb-2">Enhanced Access</h3>
              <p className="text-xs text-gray-500">
                For private games and advanced features
              </p>
            </div>
            
            <button
              disabled
              className="w-full bg-gray-700 text-gray-400 py-3 px-4 rounded-lg cursor-not-allowed font-medium flex items-center justify-center space-x-2"
              title="OAuth integration not yet available from Chess.com"
            >
              <div className="text-lg">🔐</div>
              <span>Connect with Chess.com OAuth</span>
              <div className="text-xs bg-gray-600 px-2 py-1 rounded">
                Coming Soon
              </div>
            </button>
            
            <div className="mt-3 text-center">
              <p className="text-xs text-gray-500">
                🔍 <strong>Note:</strong> Chess.com doesn't currently offer OAuth for third-party apps.
                <br />
                We're using public API access for your games and analysis.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
