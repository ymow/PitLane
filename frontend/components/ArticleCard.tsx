import React from 'react';

export interface Article {
    id?: number;
    slug: string;
    title: string;
    excerpt?: string;
    image_url?: string;
    category?: string;
    published_at?: string;
    author?: string;
}

interface ArticleCardProps {
    article: Article;
    variant?: 'featured' | 'large' | 'medium' | 'small';
    imageClassName?: string;
}

export function ArticleCard({ article, variant = 'medium', imageClassName }: ArticleCardProps) {
    const defaultImage = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop";
    const imageUrl = article.image_url || defaultImage;

    // Featured — full width with gradient overlay
    if (variant === 'featured') {
        return (
            <div className="relative hover-img max-h-98 overflow-hidden">
                <a href={`/article/${article.slug}`}>
                    <img
                        className={imageClassName || "max-w-full w-full mx-auto h-auto"}
                        src={imageUrl}
                        alt={article.title}
                    />
                </a>
                <div className="absolute px-5 pt-8 pb-5 bottom-0 w-full bg-gradient-cover">
                    <a href={`/article/${article.slug}`}>
                        <h2 className="font-display text-3xl text-white mb-3 leading-snug hover:text-f1-red-light transition-colors">
                            {article.title}
                        </h2>
                    </a>
                    {article.excerpt && (
                        <p className="text-gray-200 hidden sm:inline-block text-sm leading-relaxed">
                            {article.excerpt}
                        </p>
                    )}
                    {article.category && (
                        <div className="pt-2">
                            <span className="inline-flex items-center gap-1.5 text-sm text-gray-200">
                                <span className="inline-block h-3 border-l-2 border-f1-red"></span>
                                {article.category.display_name || article.category.name}
                            </span>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Large — similar to featured but slightly smaller
    if (variant === 'large') {
        return (
            <div className="relative hover-img max-h-98 overflow-hidden rounded-lg">
                <a href={`/article/${article.slug}`}>
                    <img
                        className={imageClassName || "max-w-full w-full mx-auto h-96 object-cover"}
                        src={imageUrl}
                        alt={article.title}
                    />
                </a>
                <div className="absolute px-5 pt-8 pb-5 bottom-0 w-full bg-gradient-cover">
                    <a href={`/article/${article.slug}`}>
                        <h2 className="font-display text-2xl text-white mb-3 leading-snug hover:text-f1-red-light transition-colors">
                            {article.title}
                        </h2>
                    </a>
                    {article.excerpt && (
                        <p className="text-gray-200 hidden sm:inline-block text-sm leading-relaxed">
                            {article.excerpt}
                        </p>
                    )}
                    {article.category && (
                        <div className="pt-2">
                            <span className="inline-flex items-center gap-1.5 text-sm text-gray-200">
                                <span className="inline-block h-3 border-l-2 border-f1-red"></span>
                                {article.category.display_name || article.category.name}
                            </span>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Medium — horizontal layout
    if (variant === 'medium') {
        return (
            <div className="flex flex-row sm:block hover-img">
                <a href={`/article/${article.slug}`} className="flex-shrink-0">
                    <img
                        className={imageClassName || "max-w-full w-full mx-auto"}
                        src={imageUrl}
                        alt={article.title}
                    />
                </a>
                <div className="py-0 sm:py-3 pl-3 sm:pl-0">
                    <h3 className="font-display text-lg leading-snug mb-2 hover:text-f1-red transition-colors">
                        <a href={`/article/${article.slug}`}>{article.title}</a>
                    </h3>
                    {article.excerpt && (
                        <p className="hidden md:block text-gray-500 text-sm leading-relaxed mb-1">
                            {article.excerpt}
                        </p>
                    )}
                    {article.category && (
                        <span className="inline-flex items-center gap-1.5 text-sm text-gray-500">
                            <span className="inline-block h-3 border-l-2 border-f1-red"></span>
                            {article.category.display_name || article.category.name}
                        </span>
                    )}
                </div>
            </div>
        );
    }

    // Small — compact horizontal
    if (variant === 'small') {
        return (
            <div className="flex flex-row items-start hover-img">
                <a href={`/article/${article.slug}`} className="flex-shrink-0 w-24 h-24 mr-3">
                    <img
                        className="w-full h-full object-cover rounded"
                        src={imageUrl}
                        alt={article.title}
                    />
                </a>
                <div className="flex-1">
                    <h4 className="font-display text-base leading-snug mb-1 hover:text-f1-red transition-colors">
                        <a href={`/article/${article.slug}`}>{article.title}</a>
                    </h4>
                    {article.category && (
                        <span className="inline-flex items-center gap-1 text-xs text-gray-500">
                            <span className="inline-block h-2 border-l-2 border-f1-red"></span>
                            {article.category.display_name || article.category.name}
                        </span>
                    )}
                </div>
            </div>
        );
    }

    return null;
}
