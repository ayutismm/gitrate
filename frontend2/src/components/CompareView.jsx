import React from 'react';
import { ArrowLeft, Trophy, TrendingUp, TrendingDown, Code, GitPullRequest, Star } from 'lucide-react';

const StatBar = ({ label, values, colors }) => {
    const max = Math.max(...values);
    return (
        <div className="space-y-2">
            <span className="text-gray-400 text-sm">{label}</span>
            <div className="space-y-1">
                {values.map((value, i) => (
                    <div key={i} className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0">
                            <img src={colors[i].avatar} alt="" className="w-full h-full object-cover" />
                        </div>
                        <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-1000 ${colors[i].color}`}
                                style={{ width: `${(value / 100) * 100}%` }}
                            />
                        </div>
                        <span className={`text-sm font-mono w-8 ${value === max ? 'text-white font-bold' : 'text-gray-400'}`}>
                            {Math.round(value)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export function CompareView({ profiles, onBack }) {
    if (!profiles || profiles.length < 2) {
        return (
            <div className="text-center p-8">
                <p className="text-gray-400">Need at least 2 profiles to compare</p>
                <button onClick={onBack} className="mt-4 text-purple-400 hover:text-purple-300">
                    Go Back
                </button>
            </div>
        );
    }

    // Sort by final score for ranking
    const ranked = [...profiles].sort((a, b) => b.final_score - a.final_score);

    const colorPalette = [
        'bg-emerald-400',
        'bg-purple-400',
        'bg-orange-400',
        'bg-blue-400',
        'bg-pink-400'
    ];

    const profileColors = profiles.map((p, i) => ({
        color: colorPalette[i % colorPalette.length],
        avatar: p.profile?.avatar_url
    }));

    return (
        <div className="w-full max-w-5xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-500">
            {/* Header */}
            <div className="flex items-center gap-4">
                <button
                    onClick={onBack}
                    className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                >
                    <ArrowLeft className="h-5 w-5 text-white" />
                </button>
                <h2 className="text-2xl font-bold text-white">Profile Comparison</h2>
            </div>

            {/* Leaderboard */}
            <div className="glass-card p-6 rounded-xl">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-yellow-400" />
                    Leaderboard
                </h3>
                <div className="space-y-3">
                    {ranked.map((profile, index) => (
                        <div
                            key={profile.profile?.username}
                            className={`flex items-center gap-4 p-3 rounded-lg ${index === 0 ? 'bg-yellow-500/10 border border-yellow-500/20' : 'bg-white/5'
                                }`}
                        >
                            <span className={`text-2xl font-bold ${index === 0 ? 'text-yellow-400' :
                                    index === 1 ? 'text-gray-300' :
                                        index === 2 ? 'text-orange-400' :
                                            'text-gray-500'
                                }`}>
                                #{index + 1}
                            </span>
                            <img
                                src={profile.profile?.avatar_url}
                                alt={profile.profile?.username}
                                className="w-12 h-12 rounded-full border-2 border-white/10"
                            />
                            <div className="flex-1">
                                <p className="text-white font-medium">{profile.profile?.name || profile.profile?.username}</p>
                                <p className="text-gray-400 text-sm">@{profile.profile?.username}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-3xl font-bold text-white">{Math.round(profile.final_score)}</p>
                                <span className={`text-xs px-2 py-0.5 rounded-full ${profile.tier === 'Elite' ? 'bg-emerald-500/20 text-emerald-400' :
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
            </div>

            {/* Score Comparison */}
            <div className="glass-card p-6 rounded-xl">
                <h3 className="text-lg font-semibold text-white mb-6">Score Breakdown</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <StatBar
                        label="Contributions"
                        values={profiles.map(p => p.contribution_score)}
                        colors={profileColors}
                    />
                    <StatBar
                        label="PR Quality"
                        values={profiles.map(p => p.pr_quality_score)}
                        colors={profileColors}
                    />
                    <StatBar
                        label="Impact"
                        values={profiles.map(p => p.impact_score)}
                        colors={profileColors}
                    />
                    <StatBar
                        label="Code Quality"
                        values={profiles.map(p => p.code_quality_score)}
                        colors={profileColors}
                    />
                </div>
            </div>

            {/* Individual Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {profiles.map((profile, i) => (
                    <div key={profile.profile?.username} className="glass-card p-4 rounded-xl">
                        <div className="flex items-center gap-3 mb-4">
                            <img
                                src={profile.profile?.avatar_url}
                                alt={profile.profile?.username}
                                className={`w-10 h-10 rounded-full border-2`}
                                style={{ borderColor: colorPalette[i % colorPalette.length].replace('bg-', '') }}
                            />
                            <div>
                                <p className="text-white font-medium text-sm">{profile.profile?.username}</p>
                                <p className="text-gray-500 text-xs">Score: {Math.round(profile.final_score)}</p>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div>
                                <p className="text-emerald-400 text-xs font-medium mb-1">Strengths</p>
                                <ul className="text-gray-400 text-xs space-y-1">
                                    {profile.strengths?.slice(0, 2).map((s, i) => (
                                        <li key={i} className="truncate">+ {s}</li>
                                    ))}
                                </ul>
                            </div>
                            <div>
                                <p className="text-orange-400 text-xs font-medium mb-1">Improvements</p>
                                <ul className="text-gray-400 text-xs space-y-1">
                                    {profile.weaknesses?.slice(0, 1).map((w, i) => (
                                        <li key={i} className="truncate">- {w}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
