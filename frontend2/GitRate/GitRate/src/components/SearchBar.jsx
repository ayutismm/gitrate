import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

export function SearchBar({ onSearch, isLoading }) {
    const [username, setUsername] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (username.trim()) {
            // Remove @ if present
            const cleanUsername = username.replace(/^@/, '');
            onSearch(cleanUsername);
        }
    };

    return (
        <div className="w-full max-w-xl mx-auto">
            <form onSubmit={handleSubmit} className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400 group-focus-within:text-white transition-colors" />
                </div>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter GitHub username..."
                    className={cn(
                        "w-full pl-11 pr-4 py-4 bg-secondary/50 border border-border rounded-xl",
                        "text-white placeholder:text-gray-500",
                        "focus:outline-none focus:ring-2 focus:ring-slate-700 focus:bg-secondary",
                        "transition-all duration-300 ease-out"
                    )}
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    className={cn(
                        "absolute right-2 top-2 bottom-2 px-4 rounded-lg font-medium",
                        "bg-white text-black hover:bg-gray-200 transition-colors",
                        "disabled:opacity-50 disabled:cursor-not-allowed",
                        "flex items-center gap-2"
                    )}
                    disabled={!username.trim() || isLoading}
                >
                    {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                        'Rate'
                    )}
                </button>
            </form>
        </div>
    );
}
