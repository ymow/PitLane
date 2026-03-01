import React, { useState } from 'react';
import { useArticles, useCategories } from '../../lib/hooks';
import { useLanguage } from '../../lib/LanguageContext';
import { ArticleCard } from '../../components/ArticleCard';
import { CategoryPills } from '../../components/CategoryPills';

export default function NewsPage() {
    const { lang } = useLanguage();
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [cursor, setCursor] = useState<string | null>(null);

    const params: Record<string, any> = { lang };
    if (selectedCategory) params.category = selectedCategory;
    if (cursor) params.cursor = cursor;

    const { data, loading, error } = useArticles(params);

    const articles = data?.results || data?.items || (Array.isArray(data) ? data : []);
    const nextCursor = data?.next;

    const handleCategoryChange = (slug: string | null) => {
        setSelectedCategory(slug);
        setCursor(null);
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

    return (
        <div className="bg-gray-50 py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-3xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 News</h1>
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
                {loading && articles.length === 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <div key={i} className="bg-white rounded-lg shadow animate-pulse h-64" />
                        ))}
                    </div>
                ) : articles.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        No articles found.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {articles.map((article: any) => (
                            <ArticleCard key={article.id} article={article} />
                        ))}
                    </div>
                )}

                {/* Load More */}
                {nextCursor && !loading && (
                    <div className="mt-8 text-center">
                        <button
                            className="px-8 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded transition-colors"
                            onClick={() => setCursor(nextCursor)}
                        >
                            Load More
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
