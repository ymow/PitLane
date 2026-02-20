import React from 'react';

export default function Page() {
    const driversStandings = [
        { pos: 1, driver: "Max Verstappen", team: "Red Bull Racing", country: "🇳🇱", points: 575, wins: 19, podiums: 21, teamColor: "#0600EF" },
        { pos: 2, driver: "Sergio Pérez", team: "Red Bull Racing", country: "🇲🇽", points: 285, wins: 2, podiums: 8, teamColor: "#0600EF" },
        { pos: 3, driver: "Lewis Hamilton", team: "Mercedes", country: "🇬🇧", points: 234, wins: 1, podiums: 5, teamColor: "#00D2BE" },
        { pos: 4, driver: "Fernando Alonso", team: "Aston Martin", country: "🇪🇸", points: 206, wins: 0, podiums: 8, teamColor: "#006F62" },
        { pos: 5, driver: "Charles Leclerc", team: "Ferrari", country: "🇲🇨", points: 206, wins: 1, podiums: 4, teamColor: "#DC143C" },
        { pos: 6, driver: "Lando Norris", team: "McLaren", country: "🇬🇧", points: 205, wins: 0, podiums: 7, teamColor: "#FF8700" },
        { pos: 7, driver: "Carlos Sainz", team: "Ferrari", country: "🇪🇸", points: 200, wins: 1, podiums: 6, teamColor: "#DC143C" },
        { pos: 8, driver: "George Russell", team: "Mercedes", country: "🇬🇧", points: 175, wins: 1, podiums: 4, teamColor: "#00D2BE" },
        { pos: 9, driver: "Oscar Piastri", team: "McLaren", country: "🇦🇺", points: 97, wins: 0, podiums: 2, teamColor: "#FF8700" },
        { pos: 10, driver: "Lance Stroll", team: "Aston Martin", country: "🇨🇦", points: 74, wins: 0, podiums: 1, teamColor: "#006F62" },
        { pos: 11, driver: "Pierre Gasly", team: "Alpine", country: "🇫🇷", points: 62, wins: 0, podiums: 0, teamColor: "#0090FF" },
        { pos: 12, driver: "Esteban Ocon", team: "Alpine", country: "🇫🇷", points: 58, wins: 0, podiums: 0, teamColor: "#0090FF" },
        { pos: 13, driver: "Alex Albon", team: "Williams", country: "🇹🇭", points: 27, wins: 0, podiums: 0, teamColor: "#005AFF" },
        { pos: 14, driver: "Yuki Tsunoda", team: "RB", country: "🇯🇵", points: 17, wins: 0, podiums: 0, teamColor: "#6692FF" },
        { pos: 15, driver: "Valtteri Bottas", team: "Kick Sauber", country: "🇫🇮", points: 10, wins: 0, podiums: 0, teamColor: "#52E252" },
        { pos: 16, driver: "Nico Hülkenberg", team: "Haas", country: "🇩🇪", points: 9, wins: 0, podiums: 0, teamColor: "#FFFFFF" },
        { pos: 17, driver: "Franco Colapinto", team: "Williams", country: "🇦🇷", points: 5, wins: 0, podiums: 0, teamColor: "#005AFF" },
        { pos: 18, driver: "Kevin Magnussen", team: "Haas", country: "🇩🇰", points: 3, wins: 0, podiums: 0, teamColor: "#FFFFFF" },
        { pos: 19, driver: "Zhou Guanyu", team: "Kick Sauber", country: "🇨🇳", points: 2, wins: 0, podiums: 0, teamColor: "#52E252" },
        { pos: 20, driver: "Liam Lawson", team: "RB", country: "🇳🇿", points: 2, wins: 0, podiums: 0, teamColor: "#6692FF" }
    ];

    const constructorsStandings = [
        { pos: 1, team: "Red Bull Racing", points: 860, color: "#0600EF", drivers: ["Max Verstappen", "Sergio Pérez"] },
        { pos: 2, team: "Mercedes", points: 409, color: "#00D2BE", drivers: ["Lewis Hamilton", "George Russell"] },
        { pos: 3, team: "Ferrari", points: 406, color: "#DC143C", drivers: ["Charles Leclerc", "Carlos Sainz"] },
        { pos: 4, team: "McLaren", points: 302, color: "#FF8700", drivers: ["Lando Norris", "Oscar Piastri"] },
        { pos: 5, team: "Aston Martin", points: 280, color: "#006F62", drivers: ["Fernando Alonso", "Lance Stroll"] },
        { pos: 6, team: "Alpine", points: 120, color: "#0090FF", drivers: ["Pierre Gasly", "Esteban Ocon"] },
        { pos: 7, team: "Williams", points: 32, color: "#005AFF", drivers: ["Alex Albon", "Franco Colapinto"] },
        { pos: 8, team: "RB", points: 19, color: "#6692FF", drivers: ["Yuki Tsunoda", "Liam Lawson"] },
        { pos: 9, team: "Haas", points: 12, color: "#FFFFFF", drivers: ["Nico Hülkenberg", "Kevin Magnussen"] },
        { pos: 10, team: "Kick Sauber", points: 12, color: "#52E252", drivers: ["Valtteri Bottas", "Zhou Guanyu"] }
    ];

    const getPositionChange = (pos: number) => {
        // Simulated position changes for demonstration
        const changes = [0, +2, -1, +1, +3, -2, 0, +1, +4, -1, +2, 0, -3, +1, +2, -1, 0, -2, +1, 0];
        return changes[pos - 1] || 0;
    };

    const getPositionChangeIcon = (change: number) => {
        if (change > 0) return <span className="text-green-500">↗</span>;
        if (change < 0) return <span className="text-red-500">↘</span>;
        return <span className="text-gray-400">→</span>;
    };

    return (
        <div className="bg-white py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Standings 2025</h1>
                    <p className="text-gray-600 text-lg">Current championship standings for drivers and constructors</p>
                </div>

                {/* Championship Leader Highlight */}
                <div className="mb-12 bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-6 border border-yellow-200">
                    <h2 className="text-2xl font-bold mb-4 flex items-center">
                        <span className="mr-2">🏆</span>
                        Championship Leader
                    </h2>
                    <div className="bg-white rounded-lg p-6 shadow-md border-l-4" style={{borderLeftColor: driversStandings[0].teamColor}}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <span className="text-4xl mr-4">{driversStandings[0].country}</span>
                                <div>
                                    <h3 className="text-2xl font-bold text-gray-900">{driversStandings[0].driver}</h3>
                                    <p className="text-gray-600">{driversStandings[0].team}</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-3xl font-bold text-yellow-600 mb-1">{driversStandings[0].points}</div>
                                <div className="text-sm text-gray-600">points</div>
                            </div>
                        </div>
                    </div>
                </div>

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
                                        {driversStandings.slice(0, 10).map((driver, index) => (
                                            <tr key={index} className="hover:bg-gray-50">
                                                <td className="px-4 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <span className="text-sm font-bold text-gray-900 mr-2">{driver.pos}</span>
                                                        {getPositionChangeIcon(getPositionChange(driver.pos))}
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <span className="text-lg mr-3">{driver.country}</span>
                                                        <div>
                                                            <div className="text-sm font-bold text-gray-900">{driver.driver}</div>
                                                            <div className="text-xs text-gray-500">{driver.team}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4 whitespace-nowrap text-right">
                                                    <span className="text-lg font-bold text-gray-900">{driver.points}</span>
                                                </td>
                                                <td className="px-4 py-4 whitespace-nowrap text-right">
                                                    <span className="text-sm text-gray-900">{driver.wins}</span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                            <div className="px-4 py-3 bg-gray-50 border-t">
                                <button className="text-red-600 hover:text-red-800 text-sm font-medium">
                                    View Full Standings →
                                </button>
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
                                        {constructorsStandings.map((team, index) => (
                                            <tr key={index} className="hover:bg-gray-50">
                                                <td className="px-4 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <span className="text-sm font-bold text-gray-900 mr-2">{team.pos}</span>
                                                        {getPositionChangeIcon(getPositionChange(team.pos))}
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <div className="w-4 h-4 rounded-full mr-3" style={{backgroundColor: team.color}}></div>
                                                        <div>
                                                            <div className="text-sm font-bold text-gray-900">{team.team}</div>
                                                            <div className="text-xs text-gray-500">
                                                                {team.drivers.join(', ')}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-4 whitespace-nowrap text-right">
                                                    <span className="text-lg font-bold text-gray-900">{team.points}</span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Championship Stats */}
                <div className="mt-12 bg-gray-50 rounded-lg p-6">
                    <h3 className="text-2xl font-bold mb-6 border-l-4 border-red-600 pl-4">Championship Statistics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">{driversStandings[0].wins}</div>
                            <div className="text-gray-600">Leader Wins</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">{driversStandings[0].points - driversStandings[1].points}</div>
                            <div className="text-gray-600">Points Gap</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">
                                {driversStandings.filter(d => d.wins > 0).length}
                            </div>
                            <div className="text-gray-600">Different Winners</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">22</div>
                            <div className="text-gray-600">Races Completed</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}