import React from 'react';
import { useF1LiveData, useRealTimeUpdates } from '../lib/hooks';

export function LiveTicker() {
  const { data, loading, error } = useF1LiveData();
  const lastUpdate = useRealTimeUpdates(60000); // Update every minute

  if (loading) {
    return (
      <div className="bg-red-600 text-white py-2">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            <span className="text-sm">Loading live updates...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-600 text-white py-2">
        <div className="container mx-auto px-4">
          <div className="text-sm text-center">
            🔴 Live updates unavailable
          </div>
        </div>
      </div>
    );
  }

  const leader = data?.standings?.drivers?.[0];
  const nextRace = data?.next_race;
  const progress = data?.season_progress;

  return (
    <div className="bg-red-600 text-white py-2 overflow-hidden">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></span>
              LIVE
            </span>
            
            {leader && (
              <span className="hidden sm:inline">
                🏆 Championship Leader: <strong>{leader.driver.first_name} {leader.driver.last_name}</strong> ({leader.points} pts)
              </span>
            )}
            
            {nextRace && (
              <span className="hidden md:inline">
                📅 Next: <strong>{nextRace.name}</strong> - {new Date(nextRace.date).toLocaleDateString()}
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-4 text-xs">
            {progress && (
              <span className="hidden lg:inline">
                Season: {progress.completed_races}/{progress.total_races} races
              </span>
            )}
            <span className="text-red-200">
              Updated {new Date(lastUpdate).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}