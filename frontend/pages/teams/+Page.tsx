import React, { useMemo } from 'react';
import { useTeams, useContracts } from '../../lib/hooks';

export default function Page() {
    const { data: teamsData, loading: teamsLoading, error: teamsError } = useTeams();
    const { data: tpData, loading: tpLoading } = useContracts({ role: 'TEAM_PRINCIPAL', is_active: 'true' });
    const { data: raceData, loading: raceLoading } = useContracts({ role: 'RACE', is_active: 'true' });

    const loading = teamsLoading || tpLoading || raceLoading;

    const { teams, tpByTeam, driversByTeam } = useMemo(() => {
        const teams = Array.isArray(teamsData?.results)
            ? teamsData.results
            : Array.isArray(teamsData)
            ? teamsData
            : [];

        const tpContracts = Array.isArray(tpData?.results)
            ? tpData.results
            : Array.isArray(tpData)
            ? tpData
            : [];

        const raceContracts = Array.isArray(raceData?.results)
            ? raceData.results
            : Array.isArray(raceData)
            ? raceData
            : [];

        const tpByTeam: Record<string, string> = {};
        for (const c of tpContracts) {
            if (c.team_code) {
                tpByTeam[c.team_code] = c.person_name || c.driver_name || '';
            }
        }

        const driversByTeam: Record<string, string[]> = {};
        for (const c of raceContracts) {
            if (c.team_code) {
                if (!driversByTeam[c.team_code]) {
                    driversByTeam[c.team_code] = [];
                }
                driversByTeam[c.team_code].push(c.driver_name || c.person_name || '');
            }
        }

        return { teams, tpByTeam, driversByTeam };
    }, [teamsData, tpData, raceData]);

    if (loading) {
        return (
            <div className="bg-white py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    <div className="mb-8">
                        <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Teams 2026</h1>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {Array.from({ length: 10 }).map((_, i) => (
                            <div key={i} className="bg-gray-100 rounded-lg h-48 animate-pulse" />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (teamsError || teams.length === 0) {
        return (
            <div className="bg-white py-6">
                <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                    <div className="mb-8">
                        <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Teams 2026</h1>
                        <p className="text-gray-600 text-lg">Discover all ten Formula 1 constructors competing in the 2026 championship</p>
                    </div>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
                        <p className="text-yellow-800 text-lg font-semibold">2026 team data coming soon</p>
                        <p className="text-yellow-700 text-sm mt-2">Team registrations for the 2026 season have not been confirmed yet.</p>
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
                    <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Teams 2026</h1>
                    <p className="text-gray-600 text-lg">Discover all ten Formula 1 constructors competing in the 2026 championship</p>
                </div>

                {/* Teams Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {teams.map((team: any) => {
                        const color = team.primary_color || '#888888';
                        const tp = tpByTeam[team.code] || '—';
                        const drivers = driversByTeam[team.code] || [];

                        return (
                            <div
                                key={team.id}
                                className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden border-l-4"
                                style={{ borderLeftColor: color }}
                            >
                                {/* Team Header */}
                                <div className="p-6 border-b border-gray-100">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-3">
                                            {team.logo_url && (
                                                <img
                                                    src={team.logo_url}
                                                    alt={team.base_name}
                                                    className="w-10 h-10 object-contain"
                                                />
                                            )}
                                            <h3 className="text-2xl font-bold text-gray-900">{team.base_name}</h3>
                                        </div>
                                        <div className="w-4 h-4 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
                                    </div>

                                    <div className="text-sm text-gray-600">
                                        <span className="font-semibold">Team Principal:</span>
                                        <p>{tp}</p>
                                    </div>
                                </div>

                                {/* Drivers */}
                                <div className="p-6 pt-4">
                                    <h4 className="font-bold text-gray-900 mb-3">2026 Drivers</h4>
                                    {drivers.length > 0 ? (
                                        <div className="space-y-2">
                                            {drivers.map((name, i) => (
                                                <div key={i} className="flex items-center bg-gray-50 rounded-lg p-3">
                                                    <span className="font-medium text-gray-900">{name}</span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-400 italic">Drivers TBC</p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Statistics Section */}
                <div className="mt-12 bg-gray-50 rounded-lg p-6">
                    <h3 className="text-2xl font-bold mb-6 border-l-4 border-red-600 pl-4">2026 Season</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">10</div>
                            <div className="text-gray-600">Teams Competing</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">20</div>
                            <div className="text-gray-600">Drivers Total</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
