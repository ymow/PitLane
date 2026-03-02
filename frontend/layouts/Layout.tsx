import React, { useEffect, useRef, useState } from 'react';
import '../styles/index.css';
import { LanguageProvider, useLanguage, SUPPORTED_LANGUAGES } from '../lib/LanguageContext';

function LanguageDropdown() {
    const { lang, setLang } = useLanguage();
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!open) return;
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, [open]);

    return (
        <div ref={ref} className="relative border-l border-gray-800 hover:bg-gray-900 hidden lg:flex items-center">
            <button
                className="flex items-center gap-1 py-3 px-4 border-b-2 border-transparent text-xs font-bold text-gray-300"
                onClick={() => setOpen(!open)}
                aria-label="Select language"
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4a9.267 9.267 0 0 1 .64-1.539 6.7 6.7 0 0 1 .597-.933A7.025 7.025 0 0 0 2.255 4H4.09zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a6.958 6.958 0 0 0-.656 2.5h2.49zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5H4.847zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5H4.51zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12c.138.386.295.744.468 1.068.552 1.035 1.218 1.65 1.887 1.855V12H5.145zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11a13.652 13.652 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5H3.82zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855.173-.324.33-.682.468-1.068H8.5zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5a6.959 6.959 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5h2.49zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4a7.966 7.966 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4h2.355z"/>
                </svg>
                {lang}
            </button>
            {open && (
                <div className="absolute right-0 top-full z-50 bg-white text-gray-700 border border-gray-100 mt-1 shadow-lg py-1" style={{ minWidth: '10rem' }}>
                    {SUPPORTED_LANGUAGES.map(l => (
                        <button
                            key={l.code}
                            onClick={() => { setLang(l.code); setOpen(false); }}
                            className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors ${lang === l.code ? 'font-bold text-f1-red' : ''}`}
                        >
                            {l.label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}

function MobileLangSelector() {
    const { lang, setLang } = useLanguage();

    return (
        <div className="px-5 py-3 border-b border-gray-100">
            <p className="text-xs text-gray-400 mb-2 uppercase font-bold tracking-wide">Language</p>
            <div className="flex flex-wrap gap-1">
                {SUPPORTED_LANGUAGES.map(l => (
                    <button
                        key={l.code}
                        onClick={() => setLang(l.code)}
                        className={`px-2 py-1 text-xs rounded border transition-colors ${
                            lang === l.code
                                ? 'border-f1-red text-f1-red font-bold bg-red-50'
                                : 'border-gray-200 text-gray-500 hover:border-gray-400'
                        }`}
                    >
                        {l.code}
                    </button>
                ))}
            </div>
        </div>
    );
}

export default function Layout({ children }: { children: React.ReactNode }) {
    const [currentPath, setCurrentPath] = useState('');
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [searchOpen, setSearchOpen] = useState(false);

    useEffect(() => {
        setCurrentPath(window.location.pathname);

        const handlePathChange = () => {
            setCurrentPath(window.location.pathname);
            setMobileMenuOpen(false); // Close mobile menu on navigation
        };

        window.addEventListener('popstate', handlePathChange);

        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;

        history.pushState = function(...args) {
            originalPushState.apply(history, args);
            handlePathChange();
        };

        history.replaceState = function(...args) {
            originalReplaceState.apply(history, args);
            handlePathChange();
        };

        return () => {
            window.removeEventListener('popstate', handlePathChange);
            history.pushState = originalPushState;
            history.replaceState = originalReplaceState;
        };
    }, []);

    const navItems = [
        { path: '/', label: 'Home' },
        { path: '/drivers', label: 'Drivers' },
        { path: '/teams', label: 'Teams' },
        { path: '/races', label: 'Calendar' },
        { path: '/standings', label: 'Standings' }
    ];

    const isActive = (path: string) => currentPath === path;

    const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);
    const toggleSearch = () => setSearchOpen(!searchOpen);

    return (
        <LanguageProvider>
        <div className="text-gray-700 pt-9 sm:pt-10">
            {/* ========== HEADER ========== */}
            <header className="fixed top-0 left-0 right-0 z-50">
                <nav className="bg-black">
                    <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                        <div className="flex justify-between">
                            <div className="mx-w-10 text-2xl font-display text-white flex items-center">
                                <a href="/">PitLane</a>
                            </div>

                            <div className="flex flex-row">
                                {/* Desktop Navigation */}
                                <ul className="navbar hidden lg:flex lg:flex-row text-gray-400 text-sm items-center font-bold">
                                    {navItems.map((item) => (
                                        <li
                                            key={item.path}
                                            className={`relative border-l border-gray-800 hover:bg-gray-900 ${isActive(item.path) ? 'active' : ''}`}
                                        >
                                            <a
                                                className={`block py-3 px-6 border-b-2 ${isActive(item.path) ? 'text-white' : 'border-transparent'}`}
                                                href={item.path}
                                            >
                                                {item.label}
                                            </a>
                                        </li>
                                    ))}
                                </ul>

                                {/* Search & Mobile Menu */}
                                <div className="flex flex-row items-center text-gray-300">
                                    {/* Search Dropdown */}
                                    <div className={`search-dropdown relative border-r lg:border-l border-gray-800 hover:bg-gray-900 ${searchOpen ? 'show' : ''}`}>
                                        <button
                                            className="block py-3 px-6 border-b-2 border-transparent"
                                            onClick={toggleSearch}
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="open bi bi-search" viewBox="0 0 16 16">
                                                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"></path>
                                            </svg>
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="close bi bi-x-lg" viewBox="0 0 16 16">
                                                <path fillRule="evenodd" d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"/>
                                                <path fillRule="evenodd" d="M2.146 2.146a.5.5 0 0 0 0 .708l11 11a.5.5 0 0 0 .708-.708l-11-11a.5.5 0 0 0-.708 0Z"/>
                                            </svg>
                                        </button>
                                        <div className="dropdown-menu absolute left-auto right-0 top-full z-50 text-left bg-white text-gray-700 border border-gray-100 mt-1 p-3" style={{ minWidth: '15rem' }}>
                                            <div className="flex flex-wrap items-stretch w-full relative">
                                                <input
                                                    type="text"
                                                    className="flex-shrink flex-grow max-w-full leading-5 w-px flex-1 relative py-2 px-5 text-gray-800 bg-white border border-gray-300 focus:outline-none focus:border-gray-400 focus:ring-0"
                                                    placeholder="Search..."
                                                    aria-label="search"
                                                />
                                                <div className="flex -mr-px">
                                                    <button className="flex items-center py-2 px-5 -ml-1 leading-5 text-gray-100 bg-black hover:text-white hover:bg-gray-900 focus:outline-none focus:ring-0" type="submit">
                                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-search" viewBox="0 0 16 16">
                                                            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"></path>
                                                        </svg>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Language Dropdown (desktop) */}
                                    <LanguageDropdown />

                                    {/* Mobile Menu Button */}
                                    <div className="relative hover:bg-gray-800 block lg:hidden">
                                        <button
                                            type="button"
                                            className="menu-mobile block py-3 px-6 border-b-2 border-transparent"
                                            onClick={toggleMobileMenu}
                                        >
                                            <span className="sr-only">Mobile menu</span>
                                            <svg className="inline-block h-6 w-6 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
                                            </svg> Menu
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </nav>
            </header>

            {/* ========== MOBILE MENU ========== */}
            <div className={`side-area fixed w-full h-full inset-0 z-50 ${mobileMenuOpen ? 'show' : ''}`}>
                {/* Background Overlay */}
                <div
                    className="back-menu fixed bg-gray-900 bg-opacity-70 w-full h-full inset-x-0 top-0"
                    onClick={toggleMobileMenu}
                >
                    <div className="cursor-pointer text-white absolute right-64 p-2">
                        <svg className="bi bi-x" width="2rem" height="2rem" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fillRule="evenodd" d="M11.854 4.146a.5.5 0 010 .708l-7 7a.5.5 0 01-.708-.708l7-7a.5.5 0 01.708 0z" clipRule="evenodd"></path>
                            <path fillRule="evenodd" d="M4.146 4.146a.5.5 0 000 .708l7 7a.5.5 0 00.708-.708l-7-7a.5.5 0 00-.708 0z" clipRule="evenodd"></path>
                        </svg>
                    </div>
                </div>

                {/* Mobile Navigation */}
                <nav className={`side-menu flex flex-col right-0 w-64 fixed top-0 bg-white h-full overflow-auto z-40 ${mobileMenuOpen ? 'show' : ''}`}>
                    <div className="mb-auto">
                        <nav className="relative flex flex-wrap">
                            <div className="text-center py-4 w-full font-bold border-b border-gray-100">PITLANE F1</div>
                            <ul className="w-full float-none flex flex-col">
                                {navItems.map((item) => (
                                    <li key={item.path} className="relative">
                                        <a
                                            href={item.path}
                                            className={`block py-2 px-5 border-b border-gray-100 hover:bg-gray-50 ${isActive(item.path) ? 'text-f1-red font-bold' : ''}`}
                                        >
                                            {item.label}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </nav>
                    </div>
                    {/* Language Selector (mobile) */}
                    <MobileLangSelector />
                    {/* Copyright */}
                    <div className="py-4 px-6 text-sm mt-6 text-center">
                        <p>Copyright <a href="/" className="text-f1-red">PitLane</a> - All rights reserved</p>
                    </div>
                </nav>
            </div>

            {/* ========== MAIN CONTENT ========== */}
            <main id="content">
                {children}
            </main>

            {/* ========== FOOTER ========== */}
            <footer className="bg-black text-gray-400">
                {/* Footer Content */}
                <div className="relative pt-8 xl:pt-16 pb-6 xl:pb-12">
                    <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2 overflow-hidden">
                        <div className="flex flex-wrap flex-row lg:justify-between -mx-3">
                            {/* Brand Section */}
                            <div className="flex-shrink max-w-full w-full lg:w-2/5 px-3 lg:pr-16">
                                <div className="flex items-center mb-2">
                                    <span className="text-3xl leading-normal mb-2 font-display text-gray-100 mt-2">PitLane</span>
                                </div>
                                <p>Your ultimate source for Formula 1 news, analysis, and insights. Stay updated with the latest from the world of F1 racing.</p>
                                {/* Social Media Icons */}
                                <ul className="space-x-3 mt-6 mb-6 lg:mb-0">
                                    <li className="inline-block">
                                        <a target="_blank" className="hover:text-gray-100" rel="noopener noreferrer" href="https://twitter.com" title="Twitter">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="2rem" height="2rem" viewBox="0 0 512 512">
                                                <path fill="currentColor" d="M496,109.5a201.8,201.8,0,0,1-56.55,15.3,97.51,97.51,0,0,0,43.33-53.6,197.74,197.74,0,0,1-62.56,23.5A99.14,99.14,0,0,0,348.31,64c-54.42,0-98.46,43.4-98.46,96.9a93.21,93.21,0,0,0,2.54,22.1,280.7,280.7,0,0,1-203-101.3A95.69,95.69,0,0,0,36,130.4C36,164,53.53,193.7,80,211.1A97.5,97.5,0,0,1,35.22,199v1.2c0,47,34,86.1,79,95a100.76,100.76,0,0,1-25.94,3.4,94.38,94.38,0,0,1-18.51-1.8c12.51,38.5,48.92,66.5,92.05,67.3A199.59,199.59,0,0,1,39.5,405.6,203,203,0,0,1,16,404.2,278.68,278.68,0,0,0,166.74,448c181.36,0,280.44-147.7,280.44-275.8,0-4.2-.11-8.4-.31-12.5A198.48,198.48,0,0,0,496,109.5Z"></path>
                                            </svg>
                                        </a>
                                    </li>
                                    <li className="inline-block">
                                        <a target="_blank" className="hover:text-gray-100" rel="noopener noreferrer" href="https://youtube.com" title="Youtube">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="2rem" height="2rem" viewBox="0 0 512 512">
                                                <path fill="currentColor" d="M508.64,148.79c0-45-33.1-81.2-74-81.2C379.24,65,322.74,64,265,64H247c-57.6,0-114.2,1-169.6,3.6-40.8,0-73.9,36.4-73.9,81.4C1,184.59-.06,220.19,0,255.79q-.15,53.4,3.4,106.9c0,45,33.1,81.5,73.9,81.5,58.2,2.7,117.9,3.9,178.6,3.8q91.2.3,178.6-3.8c40.9,0,74-36.5,74-81.5,2.4-35.7,3.5-71.3,3.4-107Q512.24,202.29,508.64,148.79ZM207,353.89V157.39l145,98.2Z"></path>
                                            </svg>
                                        </a>
                                    </li>
                                    <li className="inline-block">
                                        <a target="_blank" className="hover:text-gray-100" rel="noopener noreferrer" href="https://instagram.com" title="Instagram">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="2rem" height="2rem" viewBox="0 0 512 512">
                                                <path fill="currentColor" d="M349.33,69.33a93.62,93.62,0,0,1,93.34,93.34V349.33a93.62,93.62,0,0,1-93.34,93.34H162.67a93.62,93.62,0,0,1-93.34-93.34V162.67a93.62,93.62,0,0,1,93.34-93.34H349.33m0-37.33H162.67C90.8,32,32,90.8,32,162.67V349.33C32,421.2,90.8,480,162.67,480H349.33C421.2,480,480,421.2,480,349.33V162.67C480,90.8,421.2,32,349.33,32Z"></path>
                                                <path fill="currentColor" d="M377.33,162.67a28,28,0,1,1,28-28A27.94,27.94,0,0,1,377.33,162.67Z"></path>
                                                <path fill="currentColor" d="M256,181.33A74.67,74.67,0,1,1,181.33,256,74.75,74.75,0,0,1,256,181.33M256,144A112,112,0,1,0,368,256,112,112,0,0,0,256,144Z"></path>
                                            </svg>
                                        </a>
                                    </li>
                                </ul>
                            </div>

                            {/* Footer Links */}
                            <div className="flex-shrink max-w-full w-full lg:w-3/5 px-3">
                                <div className="flex flex-wrap flex-row">
                                    <div className="flex-shrink max-w-full w-1/2 md:w-1/4 mb-6 lg:mb-0">
                                        <h4 className="text-base leading-normal mb-3 uppercase text-gray-100">Sections</h4>
                                        <ul>
                                            <li className="py-1 hover:text-white"><a href="/">Home</a></li>
                                            <li className="py-1 hover:text-white"><a href="/drivers">Drivers</a></li>
                                            <li className="py-1 hover:text-white"><a href="/teams">Teams</a></li>
                                            <li className="py-1 hover:text-white"><a href="/races">Calendar</a></li>
                                            <li className="py-1 hover:text-white"><a href="/standings">Standings</a></li>
                                        </ul>
                                    </div>
                                    <div className="flex-shrink max-w-full w-1/2 md:w-1/4 mb-6 lg:mb-0">
                                        <h4 className="text-base leading-normal mb-3 uppercase text-gray-100">Categories</h4>
                                        <ul>
                                            <li className="py-1 hover:text-white"><a href="#">Race Results</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">Team News</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">Driver Updates</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">Technical Analysis</a></li>
                                        </ul>
                                    </div>
                                    <div className="flex-shrink max-w-full w-1/2 md:w-1/4 mb-6 lg:mb-0">
                                        <h4 className="text-base leading-normal mb-3 uppercase text-gray-100">Resources</h4>
                                        <ul>
                                            <li className="py-1 hover:text-white"><a href="#">Season Schedule</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">Circuit Guide</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">F1 Regulations</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">History</a></li>
                                        </ul>
                                    </div>
                                    <div className="flex-shrink max-w-full w-1/2 md:w-1/4 mb-6 lg:mb-0">
                                        <h4 className="text-base leading-normal mb-3 uppercase text-gray-100">About</h4>
                                        <ul>
                                            <li className="py-1 hover:text-white"><a href="#">About Us</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">Contact</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">Privacy Policy</a></li>
                                            <li className="py-1 hover:text-white"><a href="#">Terms of Use</a></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer Copyright */}
                <div className="footer-dark">
                    <div className="container py-4 border-t border-gray-200 border-opacity-10">
                        <div className="text-center">
                            <p className="my-3">&copy; {new Date().getFullYear()} PitLane | Your Ultimate F1 Source | All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
        </LanguageProvider>
    );
}
