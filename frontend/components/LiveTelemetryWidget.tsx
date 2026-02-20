import React from 'react';
import { useOpenF1, OpenF1CarData } from '../lib/useOpenF1';

interface Props {
  sessionKey: number;
}

export function LiveTelemetryWidget({ sessionKey }: Props) {
  const { telemetry, error } = useOpenF1(sessionKey);
  
  // Sort drivers by speed for fun, or just number
  const drivers = Object.values(telemetry).sort((a, b) => b.speed - a.speed);
  
  if (error) {
    return <div className="text-red-500 text-xs">Live Data Unavailable</div>;
  }

  if (drivers.length === 0) {
    return <div className="text-gray-400 text-xs animate-pulse">Connecting to Live Telemetry...</div>;
  }

  return (
    <div className="bg-neutral-900 rounded-lg p-4 border border-neutral-800">
      <h3 className="text-sm font-bold text-white mb-3 flex items-center">
        <span className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></span>
        LIVE TELEMETRY (Top Speeds)
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {drivers.slice(0, 12).map((car) => (
          <div key={car.driver_number} className="bg-neutral-800 rounded p-2 text-xs">
            <div className="flex justify-between items-center mb-1">
              <span className="font-bold text-white">#{car.driver_number}</span>
              <span className="text-gray-400">{car.rpm} RPM</span>
            </div>
            <div className="flex justify-between items-end">
              <div className="text-xl font-mono text-green-400">
                {car.speed} <span className="text-[10px] text-gray-500">km/h</span>
              </div>
              <div className="text-gray-500">
                Gear {car.gear}
              </div>
            </div>
            <div className="w-full bg-gray-700 h-1 mt-2 rounded overflow-hidden">
              <div 
                className="bg-green-500 h-full transition-all duration-300" 
                style={{ width: `${car.throttle}%` }} 
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
