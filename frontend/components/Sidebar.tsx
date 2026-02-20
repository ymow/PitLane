import React from 'react';

interface SidebarProps {
    popularArticles?: Array<{
        title: string;
        slug: string;
    }>;
}

export function Sidebar({ popularArticles = [] }: SidebarProps) {
    // Default popular articles if none provided
    const defaultArticles = [
        { title: "Latest F1 Race Results and Championship Standings", slug: "latest-race-results" },
        { title: "Driver Market: Who's Moving for Next Season?", slug: "driver-market-moves" },
        { title: "Technical Analysis: The Evolution of F1 Aerodynamics", slug: "f1-aerodynamics" },
        { title: "Team Performance Review: Mid-Season Analysis", slug: "team-performance" },
        { title: "Circuit Guide: Upcoming Race Weekend Preview", slug: "circuit-guide" },
    ];

    const articles = popularArticles.length > 0 ? popularArticles : defaultArticles;

    return (
        <div className="flex-shrink max-w-full w-full lg:w-1/3 lg:pl-8 lg:pt-14 lg:pb-8 order-first lg:order-last">
            <div className="w-full bg-white">
                {/* Most Popular */}
                <div className="mb-6">
                    <div className="p-4 bg-gray-100">
                        <h2 className="text-lg font-bold">Most Popular</h2>
                    </div>
                    <ul className="post-number">
                        {articles.slice(0, 5).map((article, index) => (
                            <li key={index} className="border-b border-gray-100 hover:bg-gray-50">
                                <a
                                    className="text-lg font-bold px-6 py-3 flex flex-row items-center"
                                    href={`/article/${article.slug}`}
                                >
                                    {article.title}
                                </a>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Ad Space Placeholder */}
                <div className="text-sm py-6 sticky">
                    <div className="w-full text-center">
                        <div className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-8">
                            <p className="text-gray-500 uppercase text-xs font-semibold mb-2">Advertisement</p>
                            <p className="text-gray-400 text-sm">250 x 250</p>
                        </div>
                    </div>
                </div>

                {/* Categories Widget (Optional) */}
                <div className="mb-6">
                    <div className="p-4 bg-gray-100">
                        <h2 className="text-lg font-bold">Categories</h2>
                    </div>
                    <ul className="border-t border-gray-100">
                        <li className="border-b border-gray-100 hover:bg-gray-50">
                            <a className="px-6 py-3 flex flex-row items-center justify-between" href="#">
                                <span>Race Results</span>
                                <span className="text-gray-500 text-sm">24</span>
                            </a>
                        </li>
                        <li className="border-b border-gray-100 hover:bg-gray-50">
                            <a className="px-6 py-3 flex flex-row items-center justify-between" href="#">
                                <span>Team News</span>
                                <span className="text-gray-500 text-sm">18</span>
                            </a>
                        </li>
                        <li className="border-b border-gray-100 hover:bg-gray-50">
                            <a className="px-6 py-3 flex flex-row items-center justify-between" href="#">
                                <span>Driver Updates</span>
                                <span className="text-gray-500 text-sm">31</span>
                            </a>
                        </li>
                        <li className="border-b border-gray-100 hover:bg-gray-50">
                            <a className="px-6 py-3 flex flex-row items-center justify-between" href="#">
                                <span>Technical</span>
                                <span className="text-gray-500 text-sm">15</span>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
