import React, { useState, useEffect, useRef } from 'react';
import { useArticles } from '../../lib/hooks';
import { useLanguage } from '../../lib/LanguageContext';
import { ArticleCard } from '../../components/ArticleCard';
import { CategoryPills } from '../../components/CategoryPills';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function NewsPage() {
    const { lang } = useLanguage();
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [cursor, setCursor] = useState<string | null>(null);
    const [allArticles, setAllArticles] = useState<any[]>([]);
    const isAppendRef = useRef(false);

    // Read ?q= from URL for search mode
    const [searchQuery, setSearchQuery] = useState<string | null>(null);
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [searchLoading, setSearchLoading] = useState(false);

    useEffect(() => {
        const q = new URLSearchParams(window.location.search).get('q');
        if (q) {
            setSearchQuery(q);
            setSearchLoading(true);
            fetch(`${API_BASE}/search/?q=${encodeURIComponent(q)}&lang=${lang}`)
                .then(r => r.json())
                .then(data => setSearchResults(data.items || []))
                .catch(() => setSearchResults([]))
                .finally(() => setSearchLoading(false));
        }
    }, [lang]);

    const params: Record<string, any> = { lang };
    if (selectedCategory) params.category = selectedCategory;
    if (cursor) params.cursor = cursor;

    const { data, loading, error } = useArticles(searchQuery ? {} : params);
    const nextCursor = data?.next ?? null;

    // Accumulate articles: append on load-more, replace on category change or initial load
    useEffect(() => {
        if (!data) return;
        const incoming = data?.results || data?.items || (Array.isArray(data) ? data : []);
        if (isAppendRef.current) {
            setAllArticles(prev => [...prev, ...incoming]);
            isAppendRef.current = false;
        } else {
            setAllArticles(incoming);
        }
    }, [data]);

    const handleCategoryChange = (slug: string | null) => {
        isAppendRef.current = false;
        setSelectedCategory(slug);
        setCursor(null);
    };

    const handleLoadMore = () => {
        if (!nextCursor) return;
        isAppendRef.current = true;
        setCursor(nextCursor);
    };

    if (error) {
        return (
            <div className="bg-gray-50 py-12">
                <div className="xl:container mx-auto px-3 text-center text-red-600">
                    Failed to load articles. Please try again later.
                </div>
            </div>
        );
    }

    // Search results view
    if (searchQuery) {
        return (
            <div className="bg-gray-50 py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    <div className="mb-6 flex items-center gap-3">
                        <h1 className="font-display text-3xl border-l-4 border-f1-red pl-4">
                            Search: <span className="text-f1-red">{searchQuery}</span>
                        </h1>
                        <a href="/news" className="text-sm text-gray-500 hover:text-gray-700 ml-2">
                            ← All News
                        </a>
                    </div>
                    {searchLoading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {Array.from({ length: 6 }).map((_, i) => (
                                <div key={i} className="bg-white rounded-lg shadow animate-pulse h-64" />
                            ))}
                        </div>
                    ) : searchResults.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            No results found for "{searchQuery}".
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {searchResults.map((article: any) => (
                                <ArticleCard
                                    key={article.id || article.slug}
                                    article={article}
                                    variant="medium"
                                    imageClassName="max-w-full w-full mx-auto h-48 object-cover"
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gray-50 py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="font-display text-3xl mb-2 border-l-4 border-f1-red pl-4">F1 News</h1>
                </div>

                {/* Category Filter */}
                <div className="mb-6 bg-white rounded-lg p-3 shadow-sm">
                    <CategoryPills
                        selected={selectedCategory}
                        onSelect={handleCategoryChange}
                        lang={lang}
                    />
                </div>

                {/* Article Grid */}
                {loading && allArticles.length === 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <div key={i} className="bg-white rounded-lg shadow animate-pulse h-64" />
                        ))}
                    </div>
                ) : allArticles.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        No articles found.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {allArticles.map((article: any) => (
                            <ArticleCard
                                key={article.id || article.slug}
                                article={article}
                                variant="medium"
                                imageClassName="max-w-full w-full mx-auto h-48 object-cover"
                            />
                        ))}
                    </div>
                )}

                {/* Load More */}
                {nextCursor && !loading && (
                    <div className="mt-8 text-center">
                        <button
                            className="px-8 py-3 bg-f1-red hover:bg-f1-red-dark text-white font-semibold rounded transition-colors"
                            onClick={handleLoadMore}
                        >
                            Load More
                        </button>
                    </div>
                )}

                {/* Loading indicator for append */}
                {loading && allArticles.length > 0 && (
                    <div className="mt-8 text-center">
                        <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-f1-red border-t-transparent" />
                    </div>
                )}
            </div>
        </div>
    );
}
