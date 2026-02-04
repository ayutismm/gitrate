import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { cn } from '../lib/utils';

const STEPS = [
    "Connecting to GitHub...",
    "Fetching repository data...",
    "Analyzing code patterns...",
    "Calculating metrics...",
    "Finalizing score..."
];

export function LoadingState() {
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentStep(prev => (prev < STEPS.length - 1 ? prev + 1 : prev));
        }, 800);

        return () => clearInterval(timer);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center p-12 w-full max-w-md mx-auto">
            <div className="relative mb-8">
                <div className="absolute inset-0 bg-white/20 blur-xl rounded-full" />
                <Loader2 className="h-12 w-12 text-white animate-spin relative z-10" />
            </div>

            <div className="space-y-4 w-full">
                {STEPS.map((step, index) => {
                    const isCompleted = index < currentStep;
                    const isCurrent = index === currentStep;

                    return (
                        <div
                            key={index}
                            className={cn(
                                "flex items-center gap-3 transition-all duration-500",
                                isCompleted ? "text-green-400" : isCurrent ? "text-white" : "text-gray-600 opacity-50"
                            )}
                        >
                            {isCompleted ? (
                                <CheckCircle2 className="h-5 w-5" />
                            ) : isCurrent ? (
                                <div className="h-5 w-5 flex items-center justify-center">
                                    <div className="h-2 w-2 bg-white rounded-full animate-pulse" />
                                </div>
                            ) : (
                                <div className="h-5 w-5" /> // Spacer
                            )}
                            <span className={cn("text-sm font-medium", isCurrent && "animate-pulse")}>
                                {step}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
