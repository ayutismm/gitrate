import React from 'react';
import { cn } from '../lib/utils';
import { GitCommit, GitPullRequest, Zap, Code } from 'lucide-react';

const Card = ({ title, content, icon: Icon, delay }) => (
    <div
        className={cn(
            "glass-card p-6 rounded-xl animate-in fade-in slide-in-from-bottom-4 duration-700",
            "hover:border-slate-600 transition-colors"
        )}
        style={{ animationDelay: `${delay}ms`, animationFillMode: 'backwards' }}
    >
        <div className="flex items-start gap-4 mb-3">
            <div className="p-2 bg-white/5 rounded-lg text-white">
                <Icon className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-semibold text-white">{title}</h3>
        </div>
        <p className="text-gray-400 leading-relaxed text-sm">
            {content}
        </p>
    </div>
);

export function AnalysisCards({ analysis }) {
    if (!analysis) return null;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <Card
                title="Contribution Analysis"
                content={analysis.contribution_analysis}
                icon={GitCommit}
                delay={100}
            />
            <Card
                title="PR Quality"
                content={analysis.pr_analysis}
                icon={GitPullRequest}
                delay={200}
            />
            <Card
                title="Impact Assessment"
                content={analysis.impact_analysis}
                icon={Zap}
                delay={300}
            />
            <Card
                title="Code Quality"
                content={analysis.code_quality_analysis}
                icon={Code}
                delay={400}
            />
        </div>
    );
}
