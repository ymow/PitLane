import React from 'react';
import { usePageContext } from 'vike-react/usePageContext';
import { useArticle } from '../../../lib/hooks';
import { Sidebar } from '../../../components/Sidebar';

export default function Page() {
    const pageContext = usePageContext();
    const { slug } = pageContext.routeParams;
    const { data: article, loading, error } = useArticle(slug);

    if (loading) {
        return (
            <div className="bg-gray-50 py-12">
                <div className="xl:container mx-auto px-3 text-center">
                    <div className="animate-pulse flex flex-col items-center">
                        <div className="h-8 bg-gray-200 w-3/4 mb-4 rounded"></div>
                        <div className="h-96 bg-gray-200 w-full rounded-lg mb-8"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error || !article) {
        return (
            <div className="bg-gray-50 py-12">
                <div className="xl:container mx-auto px-3 text-center">
                    <h1 className="text-2xl font-bold text-gray-800">Article not found</h1>
                    <p className="text-gray-600 mt-2">The article you are looking for does not exist or has been moved.</p>
                    <a href="/" className="inline-block mt-4 text-red-600 font-bold">← Back to Home</a>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-gray-50 py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                <div className="flex flex-row flex-wrap">
                    {/* Left - Article Content */}
                    <div className="flex-shrink max-w-full w-full lg:w-2/3 overflow-hidden">
                        {/* Article Title */}
                        <div className="w-full py-3 mb-3">
                            <h1 className="text-gray-800 text-3xl font-bold">
                                <span className="inline-block h-5 border-l-3 border-red-600 mr-2"></span>
                                {article.title}
                            </h1>
                        </div>

                        <div className="flex flex-row flex-wrap -mx-3">
                            <div className="max-w-full w-full px-4">
                                {/* Featured Image */}
                                {article.image_url && (
                                    <figure className="mb-6">
                                        <img
                                            className="max-w-full w-full h-auto rounded-lg"
                                            src={article.image_url}
                                            alt={article.title}
                                        />
                                    </figure>
                                )}

                                {/* Article Body */}
                                <div
                                    className="leading-relaxed pb-4 prose max-w-none text-gray-700 article-body"
                                    dangerouslySetInnerHTML={{ __html: article.body }}
                                />

                                {/* Article Meta */}
                                <div className="relative flex flex-row items-center justify-between overflow-hidden bg-gray-100 mt-12 mb-2 px-6 py-2">
                                    <div className="my-4 text-sm">
                                        {/* Author */}
                                        {article.source && (
                                            <span className="mr-2 md:mr-4">
                                                <svg className="bi bi-person mr-2 inline-block" width="1rem" height="1rem" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                    <path fillRule="evenodd" d="M13 14s1 0 1-1-1-4-6-4-6 3-6 4 1 1 1 1h10zm-9.995-.944v-.002.002zM3.022 13h9.956a.274.274 0 00.014-.002l.008-.002c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664a1.05 1.05 0 00.022.004zm9.974.056v-.002.002zM8 7a2 2 0 100-4 2 2 0 000 4zm3-2a3 3 0 11-6 0 3 3 0 016 0z" clipRule="evenodd"></path>
                                                </svg>
                                                Source: <span className="font-semibold">{article.source.name}</span>
                                            </span>
                                        )}

                                        {/* Date */}
                                        <time className="mr-2 md:mr-4" dateTime={article.published_at}>
                                            <svg className="bi bi-calendar mr-2 inline-block" width="1rem" height="1rem" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                <path fillRule="evenodd" d="M14 0H2a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V2a2 2 0 00-2-2zM1 3.857C1 3.384 1.448 3 2 3h12c.552 0 1 .384 1 .857v10.286c0 .473-.448.857-1 .857H2c-.552 0-1-.384-1-.857V3.857z" clipRule="evenodd"></path>
                                                <path fillRule="evenodd" d="M6.5 7a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm-9 3a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm-9 3a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"></path>
                                            </svg>
                                            {new Date(article.published_at).toLocaleDateString('zh-TW', { month: 'short', day: 'numeric', year: 'numeric' })}
                                        </time>
                                    </div>

                                    {/* Original Link */}
                                    <div className="hidden lg:block">
                                        <a 
                                            href={article.original_url} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            className="text-red-600 hover:text-red-800 text-sm font-bold"
                                        >
                                            VIEW ORIGINAL →
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right - Sidebar */}
                    <Sidebar />
                </div>
            </div>
        </div>
    );
}
