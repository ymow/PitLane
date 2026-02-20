import React from 'react';
import { useF1Standings } from '../lib/hooks';

export function StandingsWidget() {
  const { data, loading, error } = useF1Standings();

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">Championship Standings</h3>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-gray-200 rounded"></div>
                <div className="flex-1 h-4 bg-gray-200 rounded"></div>
                <div className="w-12 h-4 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !data?.drivers) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">Championship Standings</h3>
        <div className="text-center text-gray-500 py-8">
          <p>⚠️ Unable to load standings</p>
          <button className="mt-2 text-red-600 hover:text-red-800 text-sm">
            Try again
          </button>
        </div>
      </div>
    );
  }

  const topDrivers = data.drivers.slice(0, 5);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">Championship Standings</h3>
        <span className="text-sm text-gray-500">2024 Season</span>
      </div>
      
      <div className="space-y-3">
        {topDrivers.map((standing: any, index: number) => (
          <div key={standing.driver.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="flex items-center space-x-3">
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                index === 0 ? 'bg-yellow-500' : 
                index === 1 ? 'bg-gray-400' : 
                index === 2 ? 'bg-orange-600' : 'bg-gray-300'
              }`}>
                {standing.position}
              </span>
              <div>
                <div className="font-semibold text-sm">
                  {standing.driver.first_name} {standing.driver.last_name}
                </div>
                <div className="text-xs text-gray-500">{standing.constructor.name}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-sm">{standing.points}</div>
              <div className="text-xs text-gray-500">{standing.wins} wins</div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <a 
          href="/standings" 
          className="text-red-600 hover:text-red-800 text-sm font-medium flex items-center justify-center"
        >
          View Full Standings →
        </a>
      </div>
    </div>
  );
}