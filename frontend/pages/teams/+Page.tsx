import React from 'react';

export default function Page() {
    const teams = [
        {
            name: "Red Bull Racing",
            country: "Austria",
            teamPrincipal: "Christian Horner",
            drivers: ["Max Verstappen", "Sergio Pérez"],
            championships: 6,
            color: "#0600EF",
            founded: 2005,
            base: "Milton Keynes, UK"
        },
        {
            name: "Ferrari",
            country: "Italy", 
            teamPrincipal: "Frédéric Vasseur",
            drivers: ["Charles Leclerc", "Carlos Sainz"],
            championships: 16,
            color: "#DC143C",
            founded: 1950,
            base: "Maranello, Italy"
        },
        {
            name: "Mercedes",
            country: "Germany",
            teamPrincipal: "Toto Wolff",
            drivers: ["Lewis Hamilton", "George Russell"],
            championships: 8,
            color: "#00D2BE",
            founded: 2010,
            base: "Brackley, UK"
        },
        {
            name: "McLaren",
            country: "United Kingdom",
            teamPrincipal: "Andrea Stella",
            drivers: ["Lando Norris", "Oscar Piastri"],
            championships: 12,
            color: "#FF8700",
            founded: 1966,
            base: "Woking, UK"
        },
        {
            name: "Aston Martin",
            country: "United Kingdom",
            teamPrincipal: "Mike Krack",
            drivers: ["Fernando Alonso", "Lance Stroll"],
            championships: 0,
            color: "#006F62",
            founded: 2021,
            base: "Silverstone, UK"
        },
        {
            name: "Alpine",
            country: "France",
            teamPrincipal: "Bruno Famin",
            drivers: ["Pierre Gasly", "Esteban Ocon"],
            championships: 2,
            color: "#0090FF",
            founded: 2021,
            base: "Enstone, UK"
        },
        {
            name: "Williams",
            country: "United Kingdom",
            teamPrincipal: "James Vowles",
            drivers: ["Alex Albon", "Franco Colapinto"],
            championships: 9,
            color: "#005AFF",
            founded: 1977,
            base: "Grove, UK"
        },
        {
            name: "RB",
            country: "Italy",
            teamPrincipal: "Laurent Mekies",
            drivers: ["Yuki Tsunoda", "Liam Lawson"],
            championships: 0,
            color: "#6692FF",
            founded: 2006,
            base: "Faenza, Italy"
        },
        {
            name: "Kick Sauber",
            country: "Switzerland",
            teamPrincipal: "Alessandro Alunni Bravi",
            drivers: ["Valtteri Bottas", "Zhou Guanyu"],
            championships: 0,
            color: "#52E252",
            founded: 1993,
            base: "Hinwil, Switzerland"
        },
        {
            name: "Haas",
            country: "United States",
            teamPrincipal: "Ayao Komatsu",
            drivers: ["Nico Hülkenberg", "Kevin Magnussen"],
            championships: 0,
            color: "#FFFFFF",
            founded: 2016,
            base: "Kannapolis, USA"
        }
    ];

    return (
        <div className="bg-white py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Teams 2025</h1>
                    <p className="text-gray-600 text-lg">Discover all ten Formula 1 constructors competing in the 2025 championship</p>
                </div>

                {/* Teams Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
                    {teams.map((team, index) => (
                        <div key={index} className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden border-l-4" style={{borderLeftColor: team.color}}>
                            {/* Team Header */}
                            <div className="p-6 border-b border-gray-100">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-2xl font-bold text-gray-900 mb-1">{team.name}</h3>
                                        <p className="text-gray-600 flex items-center">
                                            <span className="mr-2">🏁</span>
                                            {team.base}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <div className="w-4 h-4 rounded-full" style={{backgroundColor: team.color}}></div>
                                    </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                                    <div>
                                        <span className="font-semibold">Team Principal:</span>
                                        <p>{team.teamPrincipal}</p>
                                    </div>
                                    <div>
                                        <span className="font-semibold">Founded:</span>
                                        <p>{team.founded}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Drivers */}
                            <div className="p-6 pt-4">
                                <h4 className="font-bold text-gray-900 mb-3 flex items-center">
                                    <span className="mr-2">🏎️</span>
                                    2025 Drivers
                                </h4>
                                <div className="space-y-2">
                                    {team.drivers.map((driver, dIndex) => (
                                        <div key={dIndex} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                                            <span className="font-medium text-gray-900">{driver}</span>
                                            <span className="text-xs text-gray-500">#{(index * 2) + dIndex + 1}</span>
                                        </div>
                                    ))}
                                </div>

                                {/* Championships */}
                                <div className="mt-4 pt-4 border-t border-gray-100">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">Championships Won</span>
                                        <div className="flex items-center">
                                            <span className="text-2xl font-bold text-gray-900">{team.championships}</span>
                                            {team.championships > 0 && (
                                                <span className="ml-2 text-yellow-500">🏆</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Statistics Section */}
                <div className="mt-12 bg-gray-50 rounded-lg p-6">
                    <h3 className="text-2xl font-bold mb-6 border-l-4 border-red-600 pl-4">Championship Statistics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">10</div>
                            <div className="text-gray-600">Teams Competing</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">20</div>
                            <div className="text-gray-600">Drivers Total</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">24</div>
                            <div className="text-gray-600">Race Calendar</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
