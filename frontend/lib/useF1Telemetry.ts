import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export interface TelemetryData {
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

export function useF1Telemetry(sessionKey: number | null) {
    const [telemetry, setTelemetry] = useState<Record<number, TelemetryData>>({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!sessionKey) return;

        setTelemetry({});

        const fetchData = async () => {
            try {
                const response = await axios.get(`${API_BASE}/f1/telemetry/`, {
                    params: { session_key: sessionKey }
                });

                const data = response.data;

                // Assuming backend returns a map or list.
                // If list, convert to map keyed by driver number.
                // We need to handle whatever structure we decide on.
                // For now, let's assume it returns a dict of driver_number -> data

                if (data && typeof data === 'object') {
                    setTelemetry(data);
                    setError(null);
                }
            } catch (err) {
                console.error('Telemetry Error:', err);
                // Don't set error state to avoid UI flickering
            }
        };

        // Initial fetch
        fetchData();

        // Poll every 1s
        const interval = setInterval(fetchData, 1000);

        return () => clearInterval(interval);
    }, [sessionKey]);

    return { telemetry, loading, error };
}