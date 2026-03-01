const SITE_URL = import.meta.env.VITE_SITE_URL || '';
const OG_IMAGE = `${SITE_URL}/og-default.jpg`;

export function Head() {
    return (
        <>
            <meta property="og:type" content="website" />
            <meta property="og:site_name" content="PitLane F1" />
            <meta property="og:title" content="F1 Standings | PitLane" />
            <meta property="og:description" content="Live Formula 1 driver and constructor championship standings updated after every race." />
            <meta property="og:image" content={OG_IMAGE} />
            <meta property="og:url" content={`${SITE_URL}/standings`} />
            <meta name="twitter:card" content="summary_large_image" />
            <link rel="canonical" href={`${SITE_URL}/standings`} />
        </>
    );
}
