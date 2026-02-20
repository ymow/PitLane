import React from 'react';
import { useArticles, useF1LiveData, useLiveRaceSession } from '../../lib/hooks';
import { LiveTicker } from '../../components/LiveTicker';
import { LiveTelemetryWidget } from '../../components/LiveTelemetryWidget';
import { StandingsWidget } from '../../components/StandingsWidget';
import { BreakingNews } from '../../components/BreakingNews';
import { ArticleCard } from '../../components/ArticleCard';
import { Sidebar } from '../../components/Sidebar';

export default function Page() {
    const { data: articles, loading: articlesLoading } = useArticles();
    const { data: liveData } = useF1LiveData();
    const { isLive, sessionType } = useLiveRaceSession();

    const allArticles = articles?.results || [];
    const featuredArticle = allArticles[0];
    const boxArticles = allArticles.slice(1, 5);
    const latestArticles = allArticles.slice(5, 15);

    // Get popular articles for sidebar
    const popularArticles = allArticles.slice(0, 5).map((article: any) => ({
        title: article.title,
        slug: article.slug
    }));

    return (
        <>
            {/* Live Ticker */}
            <LiveTicker />

            {/* Live Race Session Banner */}
            {isLive && (
                <div className="bg-gradient-to-r from-red-600 to-red-800 text-white py-4">
                    <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                        <div className="text-center">
                            <h2 className="text-2xl font-bold mb-2 flex items-center justify-center">
                                🔴 LIVE: {sessionType}
                            </h2>
                            <p className="text-red-100">Follow the action in real-time with live updates and timing</p>
                        </div>
                        
                        {/* Live Telemetry Widget */}
                        {liveData?.next_race?.openf1_session_key && (
                             <div className="mt-4">
                                 <LiveTelemetryWidget sessionKey={liveData.next_race.openf1_session_key} />
                             </div>
                        )}
                    </div>
                </div>
            )}

            {/* Hero Section with Featured Articles */}
            <div className="bg-white py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    {/* Main Hero Grid */}
                    <div className="flex flex-row flex-wrap">
                        {/* Left - Featured Article */}
                        <div className="flex-shrink max-w-full w-full lg:w-1/2 pb-1 lg:pb-0 lg:pr-1">
                            {articlesLoading ? (
                                <div className="animate-pulse">
                                    <div className="bg-gray-200 max-h-98 rounded"></div>
                                </div>
                            ) : featuredArticle ? (
                                <ArticleCard
                                    article={featuredArticle}
                                    variant="featured"
                                    imageClassName="max-w-full w-full mx-auto h-auto"
                                />
                            ) : (
                                <div className="bg-gray-100 max-h-98 flex items-center justify-center">
                                    <p className="text-gray-500">No featured articles available</p>
                                </div>
                            )}
                        </div>

                        {/* Right - Box of 4 Articles */}
                        <div className="flex-shrink max-w-full w-full lg:w-1/2">
                            <div className="box-one flex flex-row flex-wrap">
                                {articlesLoading ? (
                                    Array.from({ length: 4 }).map((_, i) => (
                                        <article key={i} className="flex-shrink max-w-full w-full sm:w-1/2">
                                            <div className="animate-pulse relative max-h-48 overflow-hidden bg-gray-200"></div>
                                        </article>
                                    ))
                                ) : (
                                    boxArticles.map((article: any, index: number) => (
                                        <article key={index} className="flex-shrink max-w-full w-full sm:w-1/2">
                                            <div className="relative hover-img max-h-48 overflow-hidden">
                                                <a href={`/article/${article.slug}`}>
                                                    <img
                                                        className="max-w-full w-full mx-auto h-auto"
                                                        src={article.image_url || "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"}
                                                        alt={article.title}
                                                    />
                                                </a>
                                                <div className="absolute px-4 pt-7 pb-4 bottom-0 w-full bg-gradient-cover">
                                                    <a href={`/article/${article.slug}`}>
                                                        <h2 className="text-lg font-bold capitalize leading-tight text-white mb-1">
                                                            {article.title}
                                                        </h2>
                                                    </a>
                                                    {article.category && (
                                                        <div className="pt-1">
                                                            <div className="text-gray-100">
                                                                <div className="inline-block h-3 border-l-2 border-red-600 mr-2"></div>
                                                                {article.category.display_name || article.category.name}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </article>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Breaking News & Standings Section */}
            <div className="bg-gray-50 py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <BreakingNews />
                        <StandingsWidget />
                    </div>
                </div>
            </div>

            {/* Latest News Section with Sidebar */}
            <div className="bg-gray-50 py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    <div className="flex flex-row flex-wrap">
                        {/* Left - Latest News */}
                        <div className="flex-shrink max-w-full w-full lg:w-2/3 overflow-hidden">
                            <div className="w-full py-3">
                                <h2 className="text-gray-800 text-2xl font-bold">
                                    <span className="inline-block h-5 border-l-3 border-red-600 mr-2"></span>
                                    Latest News
                                </h2>
                            </div>

                            <div className="flex flex-row flex-wrap -mx-3">
                                {articlesLoading ? (
                                    Array.from({ length: 6 }).map((_, i) => (
                                        <div key={i} className="flex-shrink max-w-full w-full sm:w-1/3 px-3 pb-3 pt-3 sm:pt-0 border-b-2 sm:border-b-0 border-dotted border-gray-100">
                                            <div className="animate-pulse">
                                                <div className="bg-gray-200 h-32 mb-3"></div>
                                                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                                                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                                            </div>
                                        </div>
                                    ))
                                ) : latestArticles.length > 0 ? (
                                    latestArticles.map((article: any) => (
                                        <div key={article.id} className="flex-shrink max-w-full w-full sm:w-1/3 px-3 pb-3 pt-3 sm:pt-0 border-b-2 sm:border-b-0 border-dotted border-gray-100">
                                            <ArticleCard article={article} variant="medium" />
                                        </div>
                                    ))
                                ) : (
                                    <div className="w-full text-center py-12">
                                        <p className="text-gray-500">No articles available</p>
                                    </div>
                                )}
                            </div>

                            {/* View More Button */}
                            {latestArticles.length > 0 && (
                                <div className="text-center mt-6">
                                    <a
                                        href="/"
                                        className="inline-block bg-black text-white px-8 py-3 hover:bg-gray-900 transition-colors font-bold uppercase text-sm"
                                    >
                                        View More Articles
                                    </a>
                                </div>
                            )}
                        </div>

                        {/* Right - Sidebar */}
                        <Sidebar popularArticles={popularArticles} />
                    </div>
                </div>
            </div>

            {/* Next Race Countdown */}
            {liveData?.next_race && (
                <div className="bg-white py-6">
                    <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                        <div className="bg-gradient-to-r from-gray-900 to-black rounded-lg p-8 text-white">
                            <div className="text-center">
                                <h2 className="text-3xl font-bold mb-6">Next Race</h2>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                                    <div>
                                        <h3 className="text-xl font-semibold mb-2">{liveData.next_race.name}</h3>
                                        <p className="text-gray-300">{liveData.next_race.circuit.name}</p>
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-semibold mb-2">Date</h3>
                                        <p className="text-gray-300">
                                            {new Date(liveData.next_race.date).toLocaleDateString('en-US', {
                                                weekday: 'long',
                                                year: 'numeric',
                                                month: 'long',
                                                day: 'numeric'
                                            })}
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-semibold mb-2">Location</h3>
                                        <p className="text-gray-300">{liveData.next_race.circuit.location}</p>
                                    </div>
                                </div>
                                <a
                                    href="/races"
                                    className="inline-block bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors uppercase text-sm"
                                >
                                    View Full Schedule
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
