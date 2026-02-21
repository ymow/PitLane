import React from 'react';
import { useCategories } from '../lib/hooks';

interface CategoryPillsProps {
    selected: string | null;
    onSelect: (slug: string | null) => void;
    lang?: string;
}

export function CategoryPills({ selected, onSelect, lang = 'zh-TW' }: CategoryPillsProps) {
    const { data, loading } = useCategories(lang);
    const categories = data?.results || data || [];

    return (
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            <button
                onClick={() => onSelect(null)}
                className={`flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    selected === null
                        ? 'bg-f1-red text-white'
                        : 'bg-white text-gray-600 border border-gray-200 hover:border-f1-red hover:text-f1-red'
                }`}
            >
                All
            </button>

            {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                    <div
                        key={i}
                        className="flex-shrink-0 h-8 w-20 rounded-full bg-gray-200 animate-pulse"
                    />
                ))
            ) : (
                categories.map((cat: any) => {
                    const label = cat.display_name || cat.name;
                    const slug = cat.slug;
                    const isActive = selected === slug;
                    return (
                        <button
                            key={slug}
                            onClick={() => onSelect(isActive ? null : slug)}
                            className={`flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
                                isActive
                                    ? 'bg-f1-red text-white'
                                    : 'bg-white text-gray-600 border border-gray-200 hover:border-f1-red hover:text-f1-red'
                            }`}
                        >
                            {label}
                        </button>
                    );
                })
            )}
        </div>
    );
}
