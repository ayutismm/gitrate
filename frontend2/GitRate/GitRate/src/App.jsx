import React, { useState } from 'react';
import { SearchBar } from './components/SearchBar';
import { Dashboard } from './components/Dashboard';
import { LoadingState } from './components/LoadingState';
import { api } from './services/api';
import { Github } from 'lucide-react';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (username) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const result = await api.rateDeveloper(username);
      setData(result);
    } catch (err) {
      console.error(err);
      setError("Failed to generate rating. Please check the username and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-primary p-6 md:p-12 overflow-x-hidden">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        {!data && !loading && (
          <div className="text-center space-y-6 animate-in fade-in slide-in-from-top-8 duration-700">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-white/5 rounded-2xl ring-1 ring-white/10">
                <Github className="h-12 w-12 text-white" />
              </div>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-gradient-to-b from-white to-white/50 bg-clip-text text-transparent">
              GitRate
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Analyze your GitHub profile and get a comprehensive developer rating based on your code quality, impact, and contributions.
            </p>
          </div>
        )}

        {/* Search - compact when data shown */}
        <div className={`transition-all duration-700 ${data || loading ? 'transform scale-90' : ''}`}>
          <SearchBar onSearch={handleSearch} isLoading={loading} />
        </div>

        {/* Content Area */}
        <div className="min-h-[400px]">
          {loading && <LoadingState />}

          {error && (
            <div className="text-center p-8 text-red-400 bg-red-500/10 rounded-xl border border-red-500/20 max-w-md mx-auto animate-in fade-in">
              <p>{error}</p>
            </div>
          )}

          {data && !loading && (
            <Dashboard data={data} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
