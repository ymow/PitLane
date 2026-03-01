const SITE_URL = import.meta.env.VITE_SITE_URL || '';
const OG_IMAGE = `${SITE_URL}/og-default.jpg`;

export function Head() {
    return (
        <>
            <meta property="og:type" content="website" />
            <meta property="og:site_name" content="PitLane F1" />
            <meta property="og:title" content="PitLane F1 | Latest Formula 1 News & Updates" />
            <meta property="og:description" content="Your ultimate source for Formula 1 news, race results, driver standings, team updates, and live race coverage." />
            <meta property="og:image" content={OG_IMAGE} />
            <meta property="og:url" content={SITE_URL || '/'} />
            <meta name="twitter:card" content="summary_large_image" />
            <link rel="canonical" href={`${SITE_URL}/`} />
        </>
    );
}
