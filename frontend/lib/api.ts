/**
 * API utilities for PitLane F1 News Platform
 * Handles all API communication with Django backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export interface ApiError {
  message: string;
  status?: number;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // News API
  async getArticles(params?: { lang?: string; category?: string; driver?: string; team?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.lang) searchParams.append('lang', params.lang);
    if (params?.category) searchParams.append('category', params.category);
    if (params?.driver) searchParams.append('driver', params.driver);
    if (params?.team) searchParams.append('team', params.team);
    
    const query = searchParams.toString();
    return this.request(`/articles/${query ? `?${query}` : ''}`);
  }

  async getArticle(slug: string, lang = 'en') {
    return this.request(`/articles/${slug}/?lang=${lang}`);
  }

  async getBreakingNews(lang = 'en', limit = 5) {
    return this.request(`/articles/breaking/?lang=${lang}&limit=${limit}`);
  }

  async searchArticles(query: string, lang = 'en', limit = 20) {
    return this.request(`/search/?q=${encodeURIComponent(query)}&lang=${lang}&limit=${limit}`);
  }

  // F1 Live Data API
  async getF1LiveData() {
    return this.request('/f1/live/');
  }

  async getF1Standings() {
    return this.request('/f1/standings/');
  }

  async getF1Schedule(year?: string) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/f1/schedule/${params}`);
  }

  async getF1RaceResults(year?: string, round?: string) {
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    if (round) params.append('round', round);
    const query = params.toString();
    return this.request(`/f1/results/${query ? `?${query}` : ''}`);
  }

  async getF1Drivers(year?: string) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/f1/drivers/${params}`);
  }

  async getF1Constructors(year?: string) {
    const params = year ? `?year=${year}` : '';
    return this.request(`/f1/constructors/${params}`);
  }

  async getF1Qualifying(year?: string, round?: string) {
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    if (round) params.append('round', round);
    const query = params.toString();
    return this.request(`/f1/qualifying/${query ? `?${query}` : ''}`);
  }

  // Legacy API endpoints (for existing functionality)
  async getDrivers() {
    return this.request('/drivers/');
  }

  async getDriver(code: string) {
    return this.request(`/drivers/${code}/`);
  }

  async getTeams() {
    return this.request('/teams/');
  }

  async getTeam(code: string) {
    return this.request(`/teams/${code}/`);
  }
}

// Singleton instance
export const apiClient = new ApiClient();

// React hooks for data fetching
export const useApi = () => {
  return apiClient;
};

// Helper types for F1 data
export interface F1Driver {
  id: string;
  code: string;
  number: string;
  first_name: string;
  last_name: string;
  nationality: string;
  date_of_birth?: string;
  url?: string;
}

export interface F1Constructor {
  id: string;
  name: string;
  nationality: string;
  url?: string;
}

export interface F1Race {
  round: number;
  name: string;
  date: string;
  time?: string;
  circuit: {
    id: string;
    name: string;
    location: string;
    coordinates: {
      lat: number;
      lng: number;
    };
  };
  url?: string;
}

export interface F1DriverStanding {
  position: number;
  points: number;
  wins: number;
  driver: F1Driver;
  constructor: F1Constructor;
}

export interface F1ConstructorStanding {
  position: number;
  points: number;
  wins: number;
  constructor: F1Constructor;
}

export interface F1LiveData {
  standings: {
    drivers: F1DriverStanding[];
    constructors: F1ConstructorStanding[];
  };
  next_race: F1Race | null;
  last_race: any | null;
  season_progress: {
    completed_races: number;
    total_races: number;
  };
}

// Error handling utilities
export const handleApiError = (error: unknown): ApiError => {
  if (error instanceof Error) {
    return {
      message: error.message,
    };
  }
  
  return {
    message: 'An unknown error occurred',
  };
};

// Cache utilities for better performance
class ApiCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();

  set(key: string, data: any, ttlSeconds = 300) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlSeconds * 1000,
    });
  }

  get(key: string) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  clear() {
    this.cache.clear();
  }
}

export const apiCache = new ApiCache();