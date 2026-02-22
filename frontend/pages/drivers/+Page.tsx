import React, { useMemo } from 'react';
import { useDrivers, useContracts } from '../../lib/hooks';

export default function Page() {
    const { data: driversData, loading: driversLoading, error: driversError } = useDrivers();
    const { data: contractsData, loading: contractsLoading } = useContracts({ role: 'RACE', is_active: 'true' });

    const loading = driversLoading || contractsLoading;

    const { drivers, teamColorByDriver } = useMemo(() => {
        const drivers = Array.isArray(driversData?.results)
            ? driversData.results
            : Array.isArray(driversData)
            ? driversData
            : [];

        const contracts = Array.isArray(contractsData?.results)
            ? contractsData.results
            : Array.isArray(contractsData)
            ? contractsData
            : [];

        const teamColorByDriver: Record<string, { team_code: string; primary_color?: string }> = {};
        for (const c of contracts) {
            if (c.driver) {
                teamColorByDriver[c.driver] = {
                    team_code: c.team_code,
                    primary_color: c.primary_color,
                };
            }
        }

        return { drivers, teamColorByDriver };
    }, [driversData, contractsData]);

    if (loading) {
        return (
            <div className="bg-white py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    <div className="mb-8">
                        <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Drivers 2026</h1>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {Array.from({ length: 20 }).map((_, i) => (
                            <div key={i} className="bg-gray-100 rounded-lg h-48 animate-pulse" />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (driversError || drivers.length === 0) {
        return (
            <div className="bg-white py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    <div className="mb-8">
                        <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Drivers 2026</h1>
                        <p className="text-gray-600 text-lg">Meet all twenty Formula 1 drivers competing in the 2026 championship</p>
                    </div>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
                        <p className="text-yellow-800 text-lg font-semibold">2026 grid data coming soon</p>
                        <p className="text-yellow-700 text-sm mt-2">Driver registrations for the 2026 season have not been confirmed yet.</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Drivers 2026</h1>
                    <p className="text-gray-600 text-lg">Meet all twenty Formula 1 drivers competing in the 2026 championship</p>
                </div>

                {/* All Drivers Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {drivers.map((driver: any) => {
                        const teamInfo = teamColorByDriver[driver.id];
                        const teamColor = teamInfo?.primary_color || '#888888';
                        const teamCode = teamInfo?.team_code || '';
                        const initials = `${driver.first_name?.[0] || ''}${driver.last_name?.[0] || ''}`;

                        return (
                            <div
                                key={driver.id}
                                className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border-l-4"
                                style={{ borderLeftColor: teamColor }}
                            >
                                {/* Driver Number badge */}
                                <div className="relative">
                                    <div className="absolute top-4 right-4 z-10">
                                        <span className="bg-black text-white text-lg font-bold px-3 py-1 rounded-full">
                                            #{driver.racing_number ?? '—'}
                                        </span>
                                    </div>

                                    {/* Avatar / Headshot */}
                                    <div className="p-6 text-center">
                                        {driver.headshot_url ? (
                                            <img
                                                src={driver.headshot_url}
                                                alt={driver.full_name}
                                                className="w-20 h-20 rounded-full mx-auto mb-4 object-cover"
                                            />
                                        ) : (
                                            <div
                                                className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center text-xl font-bold text-white"
                                                style={{ backgroundColor: teamColor }}
                                            >
                                                {initials}
                                            </div>
                                        )}

                                        <h3 className="text-lg font-bold text-gray-900 mb-1">{driver.full_name}</h3>
                                        <p className="text-sm text-gray-500">{driver.nationality}</p>
                                        {teamCode && (
                                            <p className="text-xs text-gray-400 mt-1">{teamCode}</p>
                                        )}
                                    </div>
                                </div>

                                {/* Team color bar */}
                                <div className="px-6 pb-6">
                                    <div className="w-full h-2 rounded-full" style={{ backgroundColor: teamColor }} />
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Grid Statistics */}
                <div className="mt-12 bg-gray-50 rounded-lg p-6">
                    <h3 className="text-2xl font-bold mb-6 border-l-4 border-red-600 pl-4">2026 Grid Statistics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-6">
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">{drivers.length}</div>
                            <div className="text-gray-600">Drivers</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">10</div>
                            <div className="text-gray-600">Teams</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
