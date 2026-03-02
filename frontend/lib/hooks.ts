import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { useLanguage } from './LanguageContext';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function useArticles(params = {}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  const paramsKey = useMemo(() => JSON.stringify(params), [params]);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await axios.get(`${API_BASE}/articles/`, { params });
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchArticles();
  }, [paramsKey]);

  return { data, loading, error };
}

export function useF1LiveData() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/f1/live/`);
      setData(response.data);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll every 30s
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error };
}

export function useF1Schedule(year?: number) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const params = year ? { year } : {};
        const response = await axios.get(`${API_BASE}/f1/schedule/`, { params });
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSchedule();
  }, [year]);

  return { data, loading, error };
}

export function useRealTimeUpdates(intervalMs = 1000) {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(interval);
  }, [intervalMs]);

  return now;
}

export function useLiveRaceSession() {
  const { data } = useF1LiveData();
  const [isLive, setIsLive] = useState(false);
  const [sessionType, setSessionType] = useState<string | null>(null);

  useEffect(() => {
    if (data?.next_race?.status === 'ONGOING') {
      setIsLive(true);
      setSessionType('RACE'); // Simplified, could be granular
    } else {
      setIsLive(false);
      setSessionType(null);
    }
  }, [data]);

  return { isLive, sessionType };
}

export function useBreakingNews(limit = 5) {
  const { lang } = useLanguage();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchBreaking = async () => {
      try {
        const response = await axios.get(`${API_BASE}/articles/breaking/`, { params: { limit, lang } });
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchBreaking();
  }, [limit, lang]);

  return { data, loading, error };
}

export function useF1Standings() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchStandings = async () => {
      try {
        const response = await axios.get(`${API_BASE}/f1/standings/`);
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStandings();
  }, []);

  return { data, loading, error };
}

export function useCategories() {
  const { lang } = useLanguage();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get(`${API_BASE}/categories/`, { params: { lang } });
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchCategories();
  }, [lang]);

  return { data, loading, error };
}

export function useTeams() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await axios.get(`${API_BASE}/teams/`);
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTeams();
  }, []);

  return { data, loading, error };
}

export function useDrivers() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchDrivers = async () => {
      try {
        const response = await axios.get(`${API_BASE}/drivers/`);
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDrivers();
  }, []);

  return { data, loading, error };
}

export function useContracts(params: Record<string, string | number> = {}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  const paramsKey = useMemo(() => JSON.stringify(params), [params]);

  useEffect(() => {
    const fetchContracts = async () => {
      try {
        const response = await axios.get(`${API_BASE}/contracts/`, { params });
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchContracts();
  }, [paramsKey]);

  return { data, loading, error };
}

export function useArticle(slug: string) {
  const { lang } = useLanguage();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    if (!slug) return;
    const fetchArticle = async () => {
      try {
        const response = await axios.get(`${API_BASE}/articles/${slug}/`, { params: { lang } });
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchArticle();
  }, [slug, lang]);

  return { data, loading, error };
}
