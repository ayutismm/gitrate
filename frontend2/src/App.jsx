import React, { useState, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { Dashboard } from './components/Dashboard';
import { LoadingState } from './components/LoadingState';
import { SavedProfiles } from './components/SavedProfiles';
import { CompareView } from './components/CompareView';
import { api } from './services/api';
import { storage } from './services/storage';
import { Github, Search, Users, GitCompare } from 'lucide-react';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [savedProfiles, setSavedProfiles] = useState([]);
  const [activeTab, setActiveTab] = useState('search'); // 'search' | 'saved' | 'compare'

  // Load saved profiles on mount
  useEffect(() => {
    setSavedProfiles(storage.getSavedProfiles());
  }, []);

  const handleSearch = async (username) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const result = await api.rateDeveloper(username);
      setData(result);
      // Auto-save profile after successful search
      storage.saveProfile(result);
      setSavedProfiles(storage.getSavedProfiles());
    } catch (err) {
      console.error(err);
      setError("Failed to generate rating. Please check the username and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveProfile = (username) => {
    storage.removeProfile(username);
    setSavedProfiles(storage.getSavedProfiles());
  };

  const handleSelectProfile = (profile) => {
    setData(profile);
    setActiveTab('search');
  };

  const handleClearAll = () => {
    if (window.confirm('Remove all saved profiles?')) {
      storage.clearAll();
      setSavedProfiles([]);
    }
  };

  const isCurrentSaved = data?.profile?.username
    ? storage.isProfileSaved(data.profile.username)
    : false;

  const tabs = [
    { id: 'search', label: 'Search', icon: Search },
    { id: 'saved', label: 'Saved', icon: Users, count: savedProfiles.length },
    { id: 'compare', label: 'Compare', icon: GitCompare, disabled: savedProfiles.length < 2 },
  ];

  return (
    <div className="min-h-screen bg-background text-primary p-6 md:p-12 overflow-x-hidden">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Logo & Title - Always visible */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-white/5 rounded-2xl ring-1 ring-white/10">
              <Github className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight bg-gradient-to-b from-white to-white/50 bg-clip-text text-transparent">
            GitRate
          </h1>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center">
          <div className="inline-flex bg-white/5 rounded-xl p-1 gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => !tab.disabled && setActiveTab(tab.id)}
                disabled={tab.disabled}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                    ? 'bg-white/10 text-white'
                    : tab.disabled
                      ? 'text-gray-600 cursor-not-allowed'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                <tab.icon className="h-4 w-4" />
                {tab.label}
                {tab.count !== undefined && tab.count > 0 && (
                  <span className="bg-purple-500/30 text-purple-300 text-xs px-1.5 py-0.5 rounded-full">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="min-h-[500px]">

          {/* Search Tab */}
          {activeTab === 'search' && (
            <div className="space-y-8 animate-in fade-in duration-300">
              {!data && !loading && (
                <p className="text-center text-gray-400 max-w-lg mx-auto">
                  Analyze GitHub profiles and get comprehensive developer ratings based on code quality, impact, and contributions.
                </p>
              )}

              <div className={`transition-all duration-500 ${data || loading ? 'transform scale-95' : ''}`}>
                <SearchBar onSearch={handleSearch} isLoading={loading} />
              </div>

              {loading && <LoadingState />}

              {error && (
                <div className="text-center p-8 text-red-400 bg-red-500/10 rounded-xl border border-red-500/20 max-w-md mx-auto">
                  <p>{error}</p>
                </div>
              )}

              {data && !loading && (
                <Dashboard
                  data={data}
                  onSave={() => { }}
                  isSaved={isCurrentSaved}
                />
              )}
            </div>
          )}

          {/* Saved Tab */}
          {activeTab === 'saved' && (
            <div className="animate-in fade-in duration-300">
              <SavedProfiles
                profiles={savedProfiles}
                onSelect={handleSelectProfile}
                onRemove={handleRemoveProfile}
                onCompare={() => setActiveTab('compare')}
                onClear={handleClearAll}
              />
            </div>
          )}

          {/* Compare Tab */}
          {activeTab === 'compare' && (
            <div className="animate-in fade-in duration-300">
              <CompareView
                profiles={savedProfiles}
                onBack={() => setActiveTab('saved')}
              />
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;
