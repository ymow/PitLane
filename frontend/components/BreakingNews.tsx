import React from 'react';
import { useBreakingNews } from '../lib/hooks';

export function BreakingNews() {
  const { data, loading, error } = useBreakingNews(5, 'zh-TW');

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center">
          <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></span>
          Breaking News
        </h3>
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !data?.items?.length) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center">
          <span className="w-3 h-3 bg-gray-300 rounded-full mr-2"></span>
          Breaking News
        </h3>
        <div className="text-center text-gray-500 py-8">
          <p>📰 No breaking news available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold mb-4 flex items-center">
        <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></span>
        Breaking News
      </h3>
      
      <div className="space-y-4">
        {data.items.map((article: any, index: number) => (
          <article key={article.id} className="border-b border-gray-100 last:border-0 pb-4 last:pb-0">
            <a href={`/article/${article.slug}`} className="block group">
              <h4 className="font-semibold text-sm group-hover:text-red-600 transition-colors leading-snug mb-2">
                {article.title}
              </h4>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center space-x-2">
                  {article.category && (
                    <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full font-medium">
                      {article.category.display_name || article.category.name}
                    </span>
                  )}
                  {article.priority === 'CRITICAL' && (
                    <span className="bg-red-600 text-white px-2 py-1 rounded-full font-bold">
                      🚨 URGENT
                    </span>
                  )}
                </span>
                <span>
                  {new Date(article.published_at).toLocaleTimeString()}
                </span>
              </div>
              {article.summary && (
                <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                  {article.summary}
                </p>
              )}
            </a>
          </article>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <a 
          href="/" 
          className="text-red-600 hover:text-red-800 text-sm font-medium flex items-center justify-center"
        >
          View All News →
        </a>
      </div>
    </div>
  );
}