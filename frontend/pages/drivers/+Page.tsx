import React from 'react';

export default function Page() {
    const drivers = [
        {
            name: "Max Verstappen",
            team: "Red Bull Racing",
            nationality: "Netherlands",
            number: 1,
            age: 27,
            championships: 3,
            teamColor: "#0600EF",
            country: "🇳🇱"
        },
        {
            name: "Sergio Pérez",
            team: "Red Bull Racing", 
            nationality: "Mexico",
            number: 11,
            age: 34,
            championships: 0,
            teamColor: "#0600EF",
            country: "🇲🇽"
        },
        {
            name: "Charles Leclerc",
            team: "Ferrari",
            nationality: "Monaco",
            number: 16,
            age: 27,
            championships: 0,
            teamColor: "#DC143C",
            country: "🇲🇨"
        },
        {
            name: "Carlos Sainz",
            team: "Ferrari",
            nationality: "Spain", 
            number: 55,
            age: 30,
            championships: 0,
            teamColor: "#DC143C",
            country: "🇪🇸"
        },
        {
            name: "Lewis Hamilton",
            team: "Mercedes",
            nationality: "United Kingdom",
            number: 44,
            age: 40,
            championships: 7,
            teamColor: "#00D2BE",
            country: "🇬🇧"
        },
        {
            name: "George Russell",
            team: "Mercedes",
            nationality: "United Kingdom",
            number: 63,
            age: 26,
            championships: 0,
            teamColor: "#00D2BE",
            country: "🇬🇧"
        },
        {
            name: "Lando Norris",
            team: "McLaren",
            nationality: "United Kingdom",
            number: 4,
            age: 25,
            championships: 0,
            teamColor: "#FF8700",
            country: "🇬🇧"
        },
        {
            name: "Oscar Piastri",
            team: "McLaren",
            nationality: "Australia",
            number: 81,
            age: 23,
            championships: 0,
            teamColor: "#FF8700",
            country: "🇦🇺"
        },
        {
            name: "Fernando Alonso",
            team: "Aston Martin",
            nationality: "Spain",
            number: 14,
            age: 43,
            championships: 2,
            teamColor: "#006F62",
            country: "🇪🇸"
        },
        {
            name: "Lance Stroll",
            team: "Aston Martin",
            nationality: "Canada",
            number: 18,
            age: 26,
            championships: 0,
            teamColor: "#006F62",
            country: "🇨🇦"
        },
        {
            name: "Pierre Gasly",
            team: "Alpine",
            nationality: "France",
            number: 10,
            age: 28,
            championships: 0,
            teamColor: "#0090FF",
            country: "🇫🇷"
        },
        {
            name: "Esteban Ocon",
            team: "Alpine",
            nationality: "France",
            number: 31,
            age: 28,
            championships: 0,
            teamColor: "#0090FF",
            country: "🇫🇷"
        },
        {
            name: "Alex Albon",
            team: "Williams",
            nationality: "Thailand",
            number: 23,
            age: 28,
            championships: 0,
            teamColor: "#005AFF",
            country: "🇹🇭"
        },
        {
            name: "Franco Colapinto",
            team: "Williams",
            nationality: "Argentina",
            number: 43,
            age: 21,
            championships: 0,
            teamColor: "#005AFF",
            country: "🇦🇷"
        },
        {
            name: "Yuki Tsunoda",
            team: "RB",
            nationality: "Japan",
            number: 22,
            age: 24,
            championships: 0,
            teamColor: "#6692FF",
            country: "🇯🇵"
        },
        {
            name: "Liam Lawson",
            team: "RB",
            nationality: "New Zealand",
            number: 30,
            age: 22,
            championships: 0,
            teamColor: "#6692FF",
            country: "🇳🇿"
        },
        {
            name: "Valtteri Bottas",
            team: "Kick Sauber",
            nationality: "Finland",
            number: 77,
            age: 35,
            championships: 0,
            teamColor: "#52E252",
            country: "🇫🇮"
        },
        {
            name: "Zhou Guanyu",
            team: "Kick Sauber",
            nationality: "China",
            number: 24,
            age: 25,
            championships: 0,
            teamColor: "#52E252",
            country: "🇨🇳"
        },
        {
            name: "Nico Hülkenberg",
            team: "Haas",
            nationality: "Germany",
            number: 27,
            age: 37,
            championships: 0,
            teamColor: "#FFFFFF",
            country: "🇩🇪"
        },
        {
            name: "Kevin Magnussen",
            team: "Haas",
            nationality: "Denmark",
            number: 20,
            age: 32,
            championships: 0,
            teamColor: "#FFFFFF",
            country: "🇩🇰"
        }
    ];

    const champions = drivers.filter(d => d.championships > 0).sort((a, b) => b.championships - a.championships);

    return (
        <div className="bg-white py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Drivers 2025</h1>
                    <p className="text-gray-600 text-lg">Meet all twenty Formula 1 drivers competing in the 2025 championship</p>
                </div>

                {/* World Champions Highlight */}
                <div className="mb-12 bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-6 border border-yellow-200">
                    <h2 className="text-2xl font-bold mb-4 flex items-center">
                        <span className="mr-2">🏆</span>
                        World Champions on the Grid
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {champions.map((driver, index) => (
                            <div key={index} className="bg-white rounded-lg p-4 shadow-md border-l-4" style={{borderLeftColor: driver.teamColor}}>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-2xl">{driver.country}</span>
                                    <span className="bg-yellow-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                                        {driver.championships}x Champion
                                    </span>
                                </div>
                                <h3 className="font-bold text-lg">{driver.name}</h3>
                                <p className="text-gray-600 text-sm">{driver.team} • #{driver.number}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* All Drivers Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {drivers.map((driver, index) => (
                        <div key={index} className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border-l-4" style={{borderLeftColor: driver.teamColor}}>
                            {/* Driver Number */}
                            <div className="relative">
                                <div className="absolute top-4 right-4 z-10">
                                    <span className="bg-black text-white text-lg font-bold px-3 py-1 rounded-full">
                                        #{driver.number}
                                    </span>
                                </div>
                                
                                {/* Driver Avatar */}
                                <div className="p-6 text-center">
                                    <div className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center text-4xl" style={{backgroundColor: driver.teamColor + "20"}}>
                                        {driver.country}
                                    </div>
                                    
                                    {/* Driver Info */}
                                    <h3 className="text-lg font-bold text-gray-900 mb-1">{driver.name}</h3>
                                    <p className="text-sm text-gray-600 mb-2">{driver.team}</p>
                                    <p className="text-xs text-gray-500">{driver.nationality}</p>
                                </div>
                            </div>

                            {/* Driver Stats */}
                            <div className="px-6 pb-6">
                                <div className="grid grid-cols-2 gap-4 text-center">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <div className="text-lg font-bold text-gray-900">{driver.age}</div>
                                        <div className="text-xs text-gray-600">Age</div>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <div className="text-lg font-bold text-gray-900">
                                            {driver.championships}
                                            {driver.championships > 0 && <span className="ml-1 text-yellow-500">🏆</span>}
                                        </div>
                                        <div className="text-xs text-gray-600">Titles</div>
                                    </div>
                                </div>

                                {/* Team Color Indicator */}
                                <div className="mt-4 flex items-center justify-center">
                                    <div className="w-full h-2 rounded-full" style={{backgroundColor: driver.teamColor}}></div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Grid Statistics */}
                <div className="mt-12 bg-gray-50 rounded-lg p-6">
                    <h3 className="text-2xl font-bold mb-6 border-l-4 border-red-600 pl-4">2025 Grid Statistics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">20</div>
                            <div className="text-gray-600">Drivers</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">{champions.length}</div>
                            <div className="text-gray-600">World Champions</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">{Math.round(drivers.reduce((sum, d) => sum + d.age, 0) / drivers.length)}</div>
                            <div className="text-gray-600">Average Age</div>
                        </div>
                        <div className="text-center bg-white rounded-lg p-6 shadow">
                            <div className="text-3xl font-bold text-red-600 mb-2">15</div>
                            <div className="text-gray-600">Nationalities</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
