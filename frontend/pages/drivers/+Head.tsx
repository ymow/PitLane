const SITE_URL = import.meta.env.VITE_SITE_URL || '';
const OG_IMAGE = `${SITE_URL}/og-default.jpg`;

export function Head() {
    return (
        <>
            <meta property="og:type" content="website" />
            <meta property="og:site_name" content="PitLane F1" />
            <meta property="og:title" content="F1 Drivers | PitLane" />
            <meta property="og:description" content="Complete guide to Formula 1 drivers — career stats, team contracts, lap records, and championship standings." />
            <meta property="og:image" content={OG_IMAGE} />
            <meta property="og:url" content={`${SITE_URL}/drivers`} />
            <meta name="twitter:card" content="summary_large_image" />
            <link rel="canonical" href={`${SITE_URL}/drivers`} />
        </>
    );
}
