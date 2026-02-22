import React from 'react';
import { useF1Standings } from '../../lib/hooks';

export default function Page() {
    const { data, loading, error } = useF1Standings();

    const driverStandings: any[] = data?.driver_standings ?? [];
    const constructorStandings: any[] = data?.constructor_standings ?? [];
    const hasData = driverStandings.length > 0 || constructorStandings.length > 0;

    const isEmpty = !loading && (!hasData || error);

    return (
        <div className="bg-white py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Standings 2026</h1>
                    <p className="text-gray-600 text-lg">Championship standings for drivers and constructors</p>
                </div>

                {loading && (
                    <div className="flex items-center justify-center py-24">
                        <div className="w-10 h-10 border-4 border-red-600 border-t-transparent rounded-full animate-spin" />
                    </div>
                )}

                {!loading && isEmpty && (
                    <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                        <p className="text-blue-800 text-lg font-semibold">2026 Season Standings — Season begins March 2026</p>
                        <p className="text-blue-700 text-sm mt-2">No race results yet. Check back once the season gets underway.</p>
                    </div>
                )}

                {!loading && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Drivers Championship */}
                        <div>
                            <h2 className="text-2xl font-bold mb-6 border-l-4 border-red-600 pl-4">Drivers Championship</h2>
                            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pos</th>
                                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Driver</th>
                                                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
                                                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Wins</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {hasData ? (
                                                driverStandings.slice(0, 10).map((driver: any, index: number) => (
                                                    <tr key={index} className="hover:bg-gray-50">
                                                        <td className="px-4 py-4 whitespace-nowrap">
                                                            <span className="text-sm font-bold text-gray-900">{driver.position ?? index + 1}</span>
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap">
                                                            <div>
                                                                <div className="text-sm font-bold text-gray-900">{driver.driver_name ?? driver.Driver?.familyName ?? '—'}</div>
                                                                <div className="text-xs text-gray-500">{driver.team_name ?? driver.Constructors?.[0]?.name ?? '—'}</div>
                                                            </div>
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-right">
                                                            <span className="text-lg font-bold text-gray-900">{driver.points ?? '—'}</span>
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-right">
                                                            <span className="text-sm text-gray-900">{driver.wins ?? '—'}</span>
                                                        </td>
                                                    </tr>
                                                ))
                                            ) : (
                                                Array.from({ length: 10 }).map((_, i) => (
                                                    <tr key={i} className="hover:bg-gray-50">
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-400">{i + 1}</td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-400">—</td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-400">—</td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-400">—</td>
                                                    </tr>
                                                ))
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        {/* Constructors Championship */}
                        <div>
                            <h2 className="text-2xl font-bold mb-6 border-l-4 border-red-600 pl-4">Constructors Championship</h2>
                            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pos</th>
                                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                                                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {hasData ? (
                                                constructorStandings.map((team: any, index: number) => (
                                                    <tr key={index} className="hover:bg-gray-50">
                                                        <td className="px-4 py-4 whitespace-nowrap">
                                                            <span className="text-sm font-bold text-gray-900">{team.position ?? index + 1}</span>
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap">
                                                            <div className="text-sm font-bold text-gray-900">{team.team_name ?? team.Constructor?.name ?? '—'}</div>
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-right">
                                                            <span className="text-lg font-bold text-gray-900">{team.points ?? '—'}</span>
                                                        </td>
                                                    </tr>
                                                ))
                                            ) : (
                                                Array.from({ length: 10 }).map((_, i) => (
                                                    <tr key={i} className="hover:bg-gray-50">
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-400">{i + 1}</td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-400">—</td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-400">—</td>
                                                    </tr>
                                                ))
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
