const SITE_URL = import.meta.env.VITE_SITE_URL || '';
const OG_IMAGE = `${SITE_URL}/og-default.jpg`;

export function Head() {
    return (
        <>
            <meta property="og:type" content="website" />
            <meta property="og:site_name" content="PitLane F1" />
            <meta property="og:title" content="F1 Teams | PitLane" />
            <meta property="og:description" content="All Formula 1 constructors — team profiles, driver lineups, technical specs, and championship results." />
            <meta property="og:image" content={OG_IMAGE} />
            <meta property="og:url" content={`${SITE_URL}/teams`} />
            <meta name="twitter:card" content="summary_large_image" />
            <link rel="canonical" href={`${SITE_URL}/teams`} />
        </>
    );
}
