import React from 'react';
import { usePageContext } from 'vike-react/usePageContext';
import { Sidebar } from '../../../components/Sidebar';

export default function Page() {
    const pageContext = usePageContext();
    const { slug } = pageContext.routeParams;

    // In production, you'd fetch article data from API
    // For now, showing the structure with TailNews design
    const article = {
        title: '5 Tips to Save Money Booking Your Next Hotel Room',
        category: 'Travel',
        author: 'John Doe',
        published_at: '2025-12-04',
        view_count: 1230,
        image_url: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=800&fit=crop',
        body: `
            <p class="mb-5">Aenean sodales lacus est, at ultricies augue ele ifend sit amet. Be yourself everyone else is already taken, sem mi placerat felis, ac suscip ligula ex id metus. Vivamus aliquet sit amet nisi non faucibus. Orci varius natoque penatibus et magnis dis parturient montes.</p>

            <h2 class="text-xl leading-normal mb-2 font-semibold text-gray-800">Start your Morning with Smiles</h2>
            <p class="mb-5">Integer egestas ipsum eget metus sodales consectetur. Nullam ultricies posuere cursus. Duis vitae lorem porta, venenatis nibh ac, laoreet massa. Nam risus lacus, porta eu diam id, fringilla porta risus. Aenean sit amet malesuada diam.</p>

            <figure class="text-center mb-6">
                <img class="max-w-full h-auto mx-auto rounded" src="https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&h=500&fit=crop" alt="Article image" />
                <figcaption class="text-sm text-gray-500 mt-2">Beautiful landscape view</figcaption>
            </figure>

            <h3 class="text-2xl leading-normal mb-2 font-semibold text-gray-800">Key Points to Remember</h3>
            <ul class="pl-8 mb-4">
                <li class="list-disc list-inside">At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium</li>
                <li class="list-disc list-inside">Et harum quidem rerum facilis est et expedita distinctio</li>
                <li class="list-disc list-inside">Itaque earum rerum hic tenetur a sapiente delectus</li>
                <li class="list-disc list-inside">which of us ever undertakes laborious physical exercise</li>
            </ul>

            <p class="mb-5">Cras justo velit, ultrices vel vehicula eu, viverra in turpis. Donec lobortis at lorem ac semper. Mauris malesuada ligula in interdum pharetra. Interdum et malesuada fames ac ante ipsum primis in faucibus.</p>

            <blockquote class="relative p-4 border-l-4 border-red-700 bg-gray-100 mb-4 text-xl">
                <p class="ml-16 mb-4">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere erat a ante.</p>
                <footer class="ml-16 text-base">Quote by <cite title="Source Title">Formula 1 Expert</cite></footer>
            </blockquote>

            <p class="mb-5">Vivamus purus orci, molestie vel erat sed, consectetur posuere ligula. Vestibulum iaculis dignissim laoreet. Cras tincidunt always have Paris, at lobortis ligula laoreet. Etiam eu sapien sit amet neque aliquam consequat nec in velit.</p>

            <p class="mb-5">Fusce elementum placerat tellus id. Nulla sit amet pretium enim, in vehicula ligula. Proin nec malesuada liberoque blandit. Sed condimentum neque ligula, id dapibus enim ornare id.</p>
        `
    };

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
                                    className="leading-relaxed pb-4 prose max-w-none"
                                    dangerouslySetInnerHTML={{ __html: article.body }}
                                />

                                {/* Article Meta */}
                                <div className="relative flex flex-row items-center justify-between overflow-hidden bg-gray-100 mt-12 mb-2 px-6 py-2">
                                    <div className="my-4 text-sm">
                                        {/* Author */}
                                        <span className="mr-2 md:mr-4">
                                            <svg className="bi bi-person mr-2 inline-block" width="1rem" height="1rem" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                <path fillRule="evenodd" d="M13 14s1 0 1-1-1-4-6-4-6 3-6 4 1 1 1 1h10zm-9.995-.944v-.002.002zM3.022 13h9.956a.274.274 0 00.014-.002l.008-.002c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664a1.05 1.05 0 00.022.004zm9.974.056v-.002.002zM8 7a2 2 0 100-4 2 2 0 000 4zm3-2a3 3 0 11-6 0 3 3 0 016 0z" clipRule="evenodd"></path>
                                            </svg>
                                            by <span className="font-semibold">{article.author}</span>
                                        </span>

                                        {/* Date */}
                                        <time className="mr-2 md:mr-4" dateTime={article.published_at}>
                                            <svg className="bi bi-calendar mr-2 inline-block" width="1rem" height="1rem" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                <path fillRule="evenodd" d="M14 0H2a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V2a2 2 0 00-2-2zM1 3.857C1 3.384 1.448 3 2 3h12c.552 0 1 .384 1 .857v10.286c0 .473-.448.857-1 .857H2c-.552 0-1-.384-1-.857V3.857z" clipRule="evenodd"></path>
                                                <path fillRule="evenodd" d="M6.5 7a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm-9 3a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm-9 3a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2zm3 0a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"></path>
                                            </svg>
                                            {new Date(article.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                                        </time>

                                        {/* Views */}
                                        <span className="mr-2 md:mr-4">
                                            <svg className="bi bi-eye mr-2 inline-block" width="1rem" height="1rem" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                <path fillRule="evenodd" d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.134 13.134 0 001.66 2.043C4.12 11.332 5.88 12.5 8 12.5c2.12 0 3.879-1.168 5.168-2.457A13.134 13.134 0 0014.828 8a13.133 13.133 0 00-1.66-2.043C11.879 4.668 10.119 3.5 8 3.5c-2.12 0-3.879 1.168-5.168 2.457A13.133 13.133 0 001.172 8z" clipRule="evenodd"></path>
                                                <path fillRule="evenodd" d="M8 5.5a2.5 2.5 0 100 5 2.5 2.5 0 000-5zM4.5 8a3.5 3.5 0 117 0 3.5 3.5 0 01-7 0z" clipRule="evenodd"></path>
                                            </svg>
                                            {article.view_count.toLocaleString()}x views
                                        </span>
                                    </div>

                                    {/* Social Share */}
                                    <div className="hidden lg:block">
                                        <ul className="space-x-3">
                                            <li className="inline-block">
                                                <a target="_blank" className="hover:text-red-700" href="#" title="Share to Facebook">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="2rem" height="2rem" viewBox="0 0 512 512">
                                                        <path fill="currentColor" d="M455.27,32H56.73A24.74,24.74,0,0,0,32,56.73V455.27A24.74,24.74,0,0,0,56.73,480H256V304H202.45V240H256V189c0-57.86,40.13-89.36,91.82-89.36,24.73,0,51.33,1.86,57.51,2.68v60.43H364.15c-28.12,0-33.48,13.3-33.48,32.9V240h67l-8.75,64H330.67V480h124.6A24.74,24.74,0,0,0,480,455.27V56.73A24.74,24.74,0,0,0,455.27,32Z"></path>
                                                    </svg>
                                                </a>
                                            </li>
                                            <li className="inline-block">
                                                <a target="_blank" className="hover:text-red-700" href="#" title="Share to Twitter">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="2rem" height="2rem" viewBox="0 0 512 512">
                                                        <path fill="currentColor" d="M496,109.5a201.8,201.8,0,0,1-56.55,15.3,97.51,97.51,0,0,0,43.33-53.6,197.74,197.74,0,0,1-62.56,23.5A99.14,99.14,0,0,0,348.31,64c-54.42,0-98.46,43.4-98.46,96.9a93.21,93.21,0,0,0,2.54,22.1,280.7,280.7,0,0,1-203-101.3A95.69,95.69,0,0,0,36,130.4C36,164,53.53,193.7,80,211.1A97.5,97.5,0,0,1,35.22,199v1.2c0,47,34,86.1,79,95a100.76,100.76,0,0,1-25.94,3.4,94.38,94.38,0,0,1-18.51-1.8c12.51,38.5,48.92,66.5,92.05,67.3A199.59,199.59,0,0,1,39.5,405.6,203,203,0,0,1,16,404.2,278.68,278.68,0,0,0,166.74,448c181.36,0,280.44-147.7,280.44-275.8,0-4.2-.11-8.4-.31-12.5A198.48,198.48,0,0,0,496,109.5Z"></path>
                                                    </svg>
                                                </a>
                                            </li>
                                        </ul>
                                    </div>
                                </div>

                                {/* Author Info (Optional) */}
                                <div className="flex flex-wrap flex-row -mx-4 justify-center py-4 mt-8 border-t border-gray-200">
                                    <div className="flex-shrink max-w-full px-4 w-1/3 sm:w-1/4 md:w-1/6">
                                        <img
                                            className="rounded-full border max-w-full h-auto"
                                            src="https://ui-avatars.com/api/?name=John+Doe&size=200&background=e11d48&color=fff"
                                            alt={article.author}
                                        />
                                    </div>
                                    <div className="flex-shrink max-w-full px-4 w-2/3 sm:w-3/4 md:w-10/12">
                                        <p className="text-lg leading-normal mb-2 font-semibold text-gray-800">
                                            {article.author}
                                        </p>
                                        <p className="text-gray-600">
                                            F1 journalist and analyst covering the latest news from the paddock.
                                        </p>
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
