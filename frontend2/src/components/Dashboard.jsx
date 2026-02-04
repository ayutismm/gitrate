import React from 'react';
import { cn } from '../lib/utils';
import { AnalysisCards } from './AnalysisCards';
import { TrendingUp, TrendingDown, Award, Bookmark, BookmarkCheck } from 'lucide-react';

const ProgressBar = ({ label, value, colorClass = "bg-white" }) => (
    <div className="space-y-2">
        <div className="flex justify-between text-sm font-medium">
            <span className="text-gray-400">{label}</span>
            <span className="text-white">{value}/100</span>
        </div>
        <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
            <div
                className={cn("h-full rounded-full transition-all duration-1000 ease-out", colorClass)}
                style={{ width: `${value}%` }}
            />
        </div>
    </div>
);

const ScoreBadge = ({ tier }) => {
    const colors = {
        Beginner: "bg-blue-500/10 text-blue-400 border-blue-500/20",
        Intermediate: "bg-purple-500/10 text-purple-400 border-purple-500/20",
        Advanced: "bg-orange-500/10 text-orange-400 border-orange-500/20",
        Elite: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    }[tier] || "bg-gray-500/10 text-gray-400 border-gray-500/20";

    return (
        <span className={cn("px-3 py-1 rounded-full text-xs font-semibold border", colors)}>
            {tier}
        </span>
    );
};

export function Dashboard({ data, onSave, isSaved }) {
    if (!data) return null;

    const {
        final_score,
        tier,
        contribution_score,
        pr_quality_score,
        impact_score,
        code_quality_score,
        strengths,
        weaknesses,
        summary,
        detailed_analysis,
        profile
    } = data;

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
            {/* Header Section */}
            <div className="glass-card p-8 rounded-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-32 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

                <div className="flex flex-col md:flex-row gap-8 items-center md:items-start relative z-10">
                    {/* Profile & Score Section */}
                    <div className="flex flex-col items-center">
                        {/* Profile Picture */}
                        {profile?.avatar_url && (
                            <div className="mb-4">
                                <img
                                    src={profile.avatar_url}
                                    alt={profile.name || profile.username}
                                    className="w-20 h-20 rounded-full border-2 border-white/20 shadow-lg"
                                />
                            </div>
                        )}

                        {/* Username & Name */}
                        {profile && (
                            <div className="text-center mb-4">
                                <h2 className="text-xl font-bold text-white">
                                    {profile.name || profile.username}
                                </h2>
                                {profile.name && profile.username && (
                                    <p className="text-sm text-gray-400">@{profile.username}</p>
                                )}
                                {profile.bio && (
                                    <p className="text-xs text-gray-500 mt-1 max-w-xs">{profile.bio}</p>
                                )}
                            </div>
                        )}

                        {/* Score Circle */}
                        <div className="w-32 h-32 rounded-full border-4 border-white/10 flex items-center justify-center bg-bg-primary relative">
                            <span className="text-5xl font-bold bg-gradient-to-br from-white to-gray-400 bg-clip-text text-transparent">
                                {Math.round(final_score)}
                            </span>
                            <div className="absolute inset-0 border-4 border-white/20 rounded-full border-t-white rotate-45" />
                        </div>
                        <div className="mt-4">
                            <ScoreBadge tier={tier} />
                        </div>
                    </div>

                    {/* Right Side: Contribution Graph + Progress Bars */}
                    <div className="flex-1 w-full space-y-6">
                        {/* GitHub Contribution Graph */}
                        {profile?.username && (
                            <div className="bg-white/5 rounded-xl p-4 overflow-hidden">
                                <p className="text-xs text-gray-500 mb-2">Contribution Activity</p>
                                <img
                                    src={`https://ghchart.rshah.org/22c55e/${profile.username}`}
                                    alt="GitHub Contribution Graph"
                                    className="w-full h-auto opacity-90"
                                    style={{ filter: 'invert(1) hue-rotate(180deg)' }}
                                    onError={(e) => { e.target.style.display = 'none' }}
                                />
                            </div>
                        )}

                        {/* Stats Grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-6">
                            <ProgressBar label="Contributions" value={contribution_score} colorClass="bg-blue-400" />
                            <ProgressBar label="PR Quality" value={pr_quality_score} colorClass="bg-purple-400" />
                            <ProgressBar label="Impact" value={impact_score} colorClass="bg-orange-400" />
                            <ProgressBar label="Code Quality" value={code_quality_score} colorClass="bg-emerald-400" />
                        </div>
                    </div>
                </div>

                {/* Tech Stack & Stats - inside header */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8 pt-8 border-t border-white/5">
                    {/* Tech Stack */}
                    <div>
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-purple-400 mb-4">
                            <Award className="h-5 w-5" /> Tech Stack
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {data.tech_stack?.length > 0 ? (
                                data.tech_stack.map(([lang, count], i) => (
                                    <span
                                        key={lang}
                                        className={`px-3 py-1.5 rounded-full text-sm font-medium ${i === 0 ? 'bg-purple-500/20 text-purple-300 ring-1 ring-purple-500/30' :
                                            i === 1 ? 'bg-blue-500/20 text-blue-300' :
                                                'bg-white/5 text-gray-400'
                                            }`}
                                    >
                                        {lang} <span className="text-xs opacity-60">({count})</span>
                                    </span>
                                ))
                            ) : (
                                <span className="text-gray-500 text-sm">No languages detected</span>
                            )}
                        </div>
                    </div>

                    {/* Stats */}
                    <div>
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-orange-400 mb-4">
                            <TrendingUp className="h-5 w-5" /> Stats
                        </h3>
                        <div className="grid grid-cols-3 gap-3">
                            <div className="bg-white/5 rounded-lg p-3 text-center">
                                <p className="text-xl font-bold text-yellow-400">{data.stats?.total_stars ?? 0}</p>
                                <p className="text-xs text-gray-500">Stars</p>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 text-center">
                                <p className="text-xl font-bold text-blue-400">{data.stats?.total_commits ?? 0}</p>
                                <p className="text-xs text-gray-500">Commits</p>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 text-center">
                                <p className="text-xl font-bold text-green-400">{data.stats?.merged_prs ?? 0}</p>
                                <p className="text-xs text-gray-500">PRs</p>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 text-center">
                                <p className="text-xl font-bold text-purple-400">{data.stats?.total_repos ?? 0}</p>
                                <p className="text-xs text-gray-500">Repos</p>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 text-center">
                                <p className="text-xl font-bold text-pink-400">{data.stats?.followers ?? 0}</p>
                                <p className="text-xs text-gray-500">Followers</p>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 text-center">
                                <p className="text-xl font-bold text-cyan-400">{data.stats?.reviews_given ?? 0}</p>
                                <p className="text-xs text-gray-500">Reviews</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Summary */}
            <div className="glass-card p-6 rounded-xl">
                <p className="text-gray-300 italic text-center text-lg leading-relaxed">
                    "{summary}"
                </p>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="glass-card p-6 rounded-xl">
                    <h3 className="flex items-center gap-2 text-lg font-semibold text-emerald-400 mb-4">
                        <TrendingUp className="h-5 w-5" /> Strengths
                    </h3>
                    <ul className="space-y-3">
                        {strengths.map((item, i) => (
                            <li key={i} className="flex gap-2 text-gray-300 text-sm">
                                <span className="text-emerald-500/50">+</span> {item}
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="glass-card p-6 rounded-xl">
                    <h3 className="flex items-center gap-2 text-lg font-semibold text-orange-400 mb-4">
                        <TrendingDown className="h-5 w-5" /> Areas for Improvement
                    </h3>
                    <ul className="space-y-3">
                        {weaknesses.map((item, i) => (
                            <li key={i} className="flex gap-2 text-gray-300 text-sm">
                                <span className="text-orange-500/50">-</span> {item}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Analysis Grid */}
            <AnalysisCards analysis={detailed_analysis} />
        </div>
    );
}
