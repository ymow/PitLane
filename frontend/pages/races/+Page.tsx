import React from 'react';
import { useF1Schedule } from '../../lib/hooks';

export default function Page() {
    const { data, loading, error } = useF1Schedule();
    const races = data?.races || [];

    const getStatusColor = (status: string, date: string) => {
        const raceDate = new Date(date);
        const today = new Date();
        
        if (raceDate < today) return 'bg-green-100 text-green-800'; // Completed
        if (Math.abs(raceDate.getTime() - today.getTime()) < 3 * 24 * 60 * 60 * 1000) return 'bg-red-100 text-red-800'; // Within 3 days
        return 'bg-blue-100 text-blue-800'; // Upcoming
    };

    const getStatusText = (date: string, status?: string) => {
        if (status === 'ONGOING') return 'LIVE';
        const raceDate = new Date(date);
        const today = new Date();
        if (raceDate < today) return 'Completed';
        return 'Upcoming';
    };

    const nextRace = races.find((race: any) => new Date(race.date) >= new Date()) || races[0];

    if (loading) {
        return (
            <div className="bg-white py-12">
                <div className="container mx-auto px-4 flex justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white py-12">
                <div className="container mx-auto px-4 text-center text-red-600">
                    Failed to load race calendar. Please try again later.
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white py-6">
            <div className="xl:container mx-auto px-3 sm:px-4 xl:px-2">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 border-l-4 border-red-600 pl-4">F1 Race Calendar {new Date().getFullYear()}</h1>
                    <p className="text-gray-600 text-lg">Complete schedule of all Formula 1 races for the season</p>
                </div>

                {/* Next Race Highlight */}
                {nextRace && (
                    <div className="mb-12 bg-gradient-to-r from-red-50 to-red-100 rounded-lg p-6 border border-red-200">
                        <h2 className="text-2xl font-bold mb-4 flex items-center">
                            <span className="mr-2">🏁</span>
                            Next Race
                        </h2>
                        <div className="bg-white rounded-lg p-6 shadow-md">
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                                <div className="flex items-center mb-4 md:mb-0">
                                    <div>
                                        <h3 className="text-2xl font-bold text-gray-900">{nextRace.name}</h3>
                                        <p className="text-gray-600">{nextRace.circuit.name}</p>
                                        <p className="text-gray-500 text-sm">{nextRace.circuit.location}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-2xl font-bold text-red-600 mb-1">
                                        {new Date(nextRace.date).toLocaleDateString()}
                                    </div>
                                    <div className="text-sm text-gray-600">Round {nextRace.round}</div>
                                    {nextRace.status === 'ONGOING' && (
                                        <span className="inline-block mt-2 px-3 py-1 bg-red-600 text-white text-xs font-bold rounded-full animate-pulse">
                                            LIVE NOW
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Full Race Calendar */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {races.map((race: any, index: number) => (
                        <div key={index} className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden">
                            {/* Race Header */}
                            <div className="p-6 border-b border-gray-100">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-2">
                                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(race.status, race.date)}`}>
                                            {getStatusText(race.date, race.status)}
                                        </span>
                                        <span className="bg-gray-100 text-gray-800 text-xs font-bold px-2 py-1 rounded-full">
                                            Round {race.round}
                                        </span>
                                    </div>
                                </div>
                                
                                <h3 className="text-xl font-bold text-gray-900 mb-2">{race.name}</h3>
                                <p className="text-gray-600 font-medium">{race.circuit.name}</p>
                                <p className="text-gray-500 text-sm">{race.circuit.location}</p>
                            </div>

                            {/* Race Details */}
                            <div className="p-6">
                                <div className="mb-4">
                                    <div className="text-lg font-bold text-red-600 mb-1">
                                        {new Date(race.date).toLocaleDateString()}
                                    </div>
                                    <div className="text-sm text-gray-500">{race.time || 'TBA'}</div>
                                </div>

                                {/* Action Button */}
                                <div className="mt-4">
                                    {race.openf1_session_key ? (
                                        <button className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded transition-colors flex items-center justify-center">
                                            <span className="mr-2">📊</span> 
                                            {race.status === 'ONGOING' ? 'Watch Live Telemetry' : 'View Analysis'}
                                        </button>
                                    ) : (
                                        <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded transition-colors">
                                            View Details
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
