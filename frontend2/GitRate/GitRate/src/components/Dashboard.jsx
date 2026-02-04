import React from 'react';
import { cn } from '../lib/utils';
import { AnalysisCards } from './AnalysisCards';
import { TrendingUp, TrendingDown, Award } from 'lucide-react';

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

export function Dashboard({ data }) {
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
        detailed_analysis
    } = data;

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
            {/* Header Section */}
            <div className="glass-card p-8 rounded-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-32 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

                <div className="flex flex-col md:flex-row gap-8 items-center md:items-start relative z-10">
                    {/* Main Score */}
                    <div className="flex flex-col items-center">
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

                    {/* Stats Grid */}
                    <div className="flex-1 w-full grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-6">
                        <ProgressBar label="Contributions" value={contribution_score} colorClass="bg-blue-400" />
                        <ProgressBar label="PR Quality" value={pr_quality_score} colorClass="bg-purple-400" />
                        <ProgressBar label="Impact" value={impact_score} colorClass="bg-orange-400" />
                        <ProgressBar label="Code Quality" value={code_quality_score} colorClass="bg-emerald-400" />
                    </div>
                </div>

                {/* Summary */}
                <div className="mt-8 pt-8 border-t border-white/5">
                    <p className="text-gray-300 italic text-center text-lg leading-relaxed">
                        "{summary}"
                    </p>
                </div>
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
