import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

export interface OpenF1CarData {
  date: string;
  driver_number: number;
  rpm: number;
  speed: number;
  throttle: number;
  brake: number;
  gear: number;
  session_key: number;
  meeting_key: number;
}

export function useOpenF1(sessionKey: number | null) {
  const [telemetry, setTelemetry] = useState<Record<number, OpenF1CarData>>({});
  const lastDateRef = useRef<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionKey) return;
    
    setTelemetry({});
    lastDateRef.current = null;

    const fetchData = async () => {
      try {
        let url = `https://api.openf1.org/v1/car_data?session_key=${sessionKey}`;
        
        // To avoid fetching full history on first load, we might want to start "now"
        // But "now" depends on server time.
        // For this prototype, let's assume we just want to see data flowing in.
        // We'll fetch whatever is available after our last check.
        // On first load, maybe we accept getting 'some' data or we try to guess 'now'.
        // Let's try to fetch with a date filter if we have one.
        
        if (lastDateRef.current) {
            url += `&date>=${lastDateRef.current}`;
        } else {
            // On first load, grab data from the last 10 minutes to ensure we get a snapshot
            const now = new Date();
            now.setMinutes(now.getMinutes() - 10);
            url += `&date>=${now.toISOString().split('.')[0]}`; // Remove milliseconds for API compatibility
        }

        const response = await axios.get<OpenF1CarData[]>(url);
        
        if (response.data.length > 0) {
            // Update last seen date
            // Assume sorted or find max
            const dates = response.data.map(d => d.date).sort();
            lastDateRef.current = dates[dates.length - 1];
            
            // Update telemetry map (latest per driver)
            setTelemetry(prev => {
                const next = { ...prev };
                response.data.forEach(d => {
                    next[d.driver_number] = d;
                });
                return next;
            });
            setError(null);
        }
      } catch (err) {
        console.error('OpenF1 Error:', err);
        // Don't set error state to avoid UI flickering, just log
      }
    };

    // Initial fetch
    fetchData();
    
    // Poll
    const interval = setInterval(fetchData, 2000);

    return () => clearInterval(interval);
  }, [sessionKey]);

  return { telemetry, loading, error };
}