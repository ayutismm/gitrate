import React, { useState } from 'react';
import { X, Users, Trash2, Filter, SortAsc, SortDesc } from 'lucide-react';

export function SavedProfiles({ profiles, onSelect, onRemove, onCompare, onClear }) {
    const [filter, setFilter] = useState('all'); // 'all' | 'Elite' | 'Advanced' | 'Intermediate' | 'Beginner'
    const [sortBy, setSortBy] = useState('date'); // 'date' | 'score' | 'name'
    const [sortOrder, setSortOrder] = useState('desc'); // 'asc' | 'desc'

    if (!profiles || profiles.length === 0) {
        return (
            <div className="glass-card p-6 rounded-xl text-center">
                <Users className="h-8 w-8 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-400 text-sm">No saved profiles yet</p>
                <p className="text-gray-500 text-xs mt-1">Search for a user - profiles are saved automatically!</p>
            </div>
        );
    }

    // Filter profiles
    let filteredProfiles = filter === 'all'
        ? profiles
        : profiles.filter(p => p.tier === filter);

    // Sort profiles
    filteredProfiles = [...filteredProfiles].sort((a, b) => {
        let comparison = 0;
        switch (sortBy) {
            case 'score':
                comparison = a.final_score - b.final_score;
                break;
            case 'name':
                const nameA = (a.profile?.name || a.profile?.username || '').toLowerCase();
                const nameB = (b.profile?.name || b.profile?.username || '').toLowerCase();
                comparison = nameA.localeCompare(nameB);
                break;
            case 'date':
            default:
                comparison = new Date(a.savedAt || 0) - new Date(b.savedAt || 0);
                break;
        }
        return sortOrder === 'desc' ? -comparison : comparison;
    });

    const tierCounts = {
        all: profiles.length,
        Elite: profiles.filter(p => p.tier === 'Elite').length,
        Advanced: profiles.filter(p => p.tier === 'Advanced').length,
        Intermediate: profiles.filter(p => p.tier === 'Intermediate').length,
        Beginner: profiles.filter(p => p.tier === 'Beginner').length,
    };

    const toggleSortOrder = () => {
        setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    };

    return (
        <div className="glass-card p-6 rounded-xl">
            {/* Header */}
            <div className="flex flex-wrap justify-between items-center gap-4 mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Saved Profiles ({profiles.length})
                </h3>
                <div className="flex gap-2">
                    {profiles.length >= 2 && (
                        <button
                            onClick={onCompare}
                            className="px-3 py-1.5 bg-purple-500/20 text-purple-400 rounded-lg text-sm hover:bg-purple-500/30 transition-colors"
                        >
                            Compare All
                        </button>
                    )}
                    <button
                        onClick={onClear}
                        className="px-3 py-1.5 bg-red-500/10 text-red-400 rounded-lg text-sm hover:bg-red-500/20 transition-colors"
                        title="Clear all"
                    >
                        <Trash2 className="h-4 w-4" />
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-2 mb-4">
                {/* Tier Filter */}
                <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
                    <Filter className="h-4 w-4 text-gray-500 ml-2" />
                    {['all', 'Elite', 'Advanced', 'Intermediate', 'Beginner'].map((tier) => (
                        <button
                            key={tier}
                            onClick={() => setFilter(tier)}
                            disabled={tierCounts[tier] === 0}
                            className={`px-2 py-1 rounded text-xs transition-colors ${filter === tier
                                    ? tier === 'Elite' ? 'bg-emerald-500/30 text-emerald-400' :
                                        tier === 'Advanced' ? 'bg-orange-500/30 text-orange-400' :
                                            tier === 'Intermediate' ? 'bg-purple-500/30 text-purple-400' :
                                                tier === 'Beginner' ? 'bg-blue-500/30 text-blue-400' :
                                                    'bg-white/20 text-white'
                                    : tierCounts[tier] === 0
                                        ? 'text-gray-600 cursor-not-allowed'
                                        : 'text-gray-400 hover:text-white hover:bg-white/10'
                                }`}
                        >
                            {tier === 'all' ? 'All' : tier} {tierCounts[tier] > 0 && `(${tierCounts[tier]})`}
                        </button>
                    ))}
                </div>

                {/* Sort Options */}
                <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="bg-transparent text-gray-400 text-xs px-2 py-1 outline-none cursor-pointer"
                    >
                        <option value="date" className="bg-zinc-900">Recent</option>
                        <option value="score" className="bg-zinc-900">Score</option>
                        <option value="name" className="bg-zinc-900">Name</option>
                    </select>
                    <button
                        onClick={toggleSortOrder}
                        className="p-1 text-gray-400 hover:text-white transition-colors"
                        title={sortOrder === 'desc' ? 'Descending' : 'Ascending'}
                    >
                        {sortOrder === 'desc' ? <SortDesc className="h-4 w-4" /> : <SortAsc className="h-4 w-4" />}
                    </button>
                </div>
            </div>

            {/* Profile Grid */}
            {filteredProfiles.length === 0 ? (
                <p className="text-center text-gray-500 text-sm py-4">No profiles match this filter</p>
            ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                    {filteredProfiles.map((profile) => (
                        <div
                            key={profile.profile?.username}
                            className="relative group bg-white/5 rounded-lg p-3 hover:bg-white/10 transition-colors cursor-pointer"
                            onClick={() => onSelect(profile)}
                        >
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onRemove(profile.profile?.username);
                                }}
                                className="absolute -top-1 -right-1 p-1 bg-red-500/80 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                <X className="h-3 w-3 text-white" />
                            </button>

                            <div className="flex flex-col items-center text-center">
                                <img
                                    src={profile.profile?.avatar_url}
                                    alt={profile.profile?.username}
                                    className="w-12 h-12 rounded-full border border-white/10 mb-2"
                                />
                                <p className="text-white text-sm font-medium truncate w-full">
                                    {profile.profile?.name || profile.profile?.username}
                                </p>
                                <p className="text-gray-500 text-xs">
                                    Score: {Math.round(profile.final_score)}
                                </p>
                                <span className={`text-xs px-2 py-0.5 rounded-full mt-1 ${profile.tier === 'Elite' ? 'bg-emerald-500/20 text-emerald-400' :
                                        profile.tier === 'Advanced' ? 'bg-orange-500/20 text-orange-400' :
                                            profile.tier === 'Intermediate' ? 'bg-purple-500/20 text-purple-400' :
                                                'bg-blue-500/20 text-blue-400'
                                    }`}>
                                    {profile.tier}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
