"""API services for external data integration."""
import requests
from datetime import datetime
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ErgastF1Service:
    """Service to interact with Ergast F1 API via Jolpica mirror."""
    
    BASE_URL = "http://api.jolpi.ca/ergast/f1"
    CURRENT_SEASON = "2026"  # Updated for 2026 season
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PitLane-F1-News/1.0'
        })
    
    def _make_request(self, endpoint, params=None):
        """Make request to Jolpica API with caching."""
        cache_key = f"jolpica:{endpoint}:{str(params) if params else 'no_params'}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            url = f"{self.BASE_URL}/{endpoint}.json"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache for different durations based on data type
            cache_duration = 3600  # 1 hour default
            if 'results' in endpoint or 'standings' in endpoint:
                cache_duration = 300  # 5 minutes for live data
            elif 'drivers' in endpoint or 'constructors' in endpoint:
                cache_duration = 86400  # 24 hours for static data
                
            cache.set(cache_key, data, cache_duration)
            return data
            
        except requests.RequestException as e:
            logger.error(f"Jolpica API request failed: {e}")
            return None

    def get_current_standings(self):
        """Get current driver and constructor standings."""
        driver_standings = self._make_request(f"{self.CURRENT_SEASON}/driverStandings")
        constructor_standings = self._make_request(f"{self.CURRENT_SEASON}/constructorStandings")
        
        return {
            'drivers': self._parse_driver_standings(driver_standings),
            'constructors': self._parse_constructor_standings(constructor_standings)
        }
    
    def _parse_driver_standings(self, data):
        """Parse driver standings data."""
        if not data or 'MRData' not in data:
            return []
            
        standings_lists = data['MRData']['StandingsTable']['StandingsLists']
        if not standings_lists:
            return []
            
        driver_standings = standings_lists[0]['DriverStandings']
        
        return [{
            'position': int(standing['position']),
            'points': float(standing['points']),
            'wins': int(standing['wins']),
            'driver': {
                'id': standing['Driver']['driverId'],
                'code': standing['Driver'].get('code', ''),
                'number': standing['Driver'].get('permanentNumber', ''),
                'first_name': standing['Driver']['givenName'],
                'last_name': standing['Driver']['familyName'],
                'nationality': standing['Driver']['nationality'],
                'date_of_birth': standing['Driver']['dateOfBirth']
            },
            'constructor': {
                'id': standing['Constructors'][0]['constructorId'],
                'name': standing['Constructors'][0]['name'],
                'nationality': standing['Constructors'][0]['nationality']
            }
        } for standing in driver_standings]
    
    def _parse_constructor_standings(self, data):
        """Parse constructor standings data."""
        if not data or 'MRData' not in data:
            return []
            
        standings_lists = data['MRData']['StandingsTable']['StandingsLists']
        if not standings_lists:
            return []
            
        constructor_standings = standings_lists[0]['ConstructorStandings']
        
        return [{
            'position': int(standing['position']),
            'points': float(standing['points']),
            'wins': int(standing['wins']),
            'constructor': {
                'id': standing['Constructor']['constructorId'],
                'name': standing['Constructor']['name'],
                'nationality': standing['Constructor']['nationality']
            }
        } for standing in constructor_standings]
    
    def get_race_schedule(self, year=None):
        """Get race schedule for the season."""
        year = year or self.CURRENT_SEASON
        data = self._make_request(f"{year}")
        
        if not data or 'MRData' not in data:
            return []
            
        races = data['MRData']['RaceTable']['Races']
        
        return [{
            'round': int(race['round']),
            'name': race['raceName'],
            'date': race['date'],
            'time': race.get('time', ''),
            'circuit': {
                'id': race['Circuit']['circuitId'],
                'name': race['Circuit']['circuitName'],
                'location': f"{race['Circuit']['Location']['locality']}, {race['Circuit']['Location']['country']}",
                'coordinates': {
                    'lat': float(race['Circuit']['Location']['lat']),
                    'lng': float(race['Circuit']['Location']['long'])
                }
            },
            'url': race['url']
        } for race in races]
    
    def get_race_results(self, year=None, round_number=None):
        """Get race results."""
        year = year or self.CURRENT_SEASON
        endpoint = f"{year}"
        
        if round_number:
            endpoint = f"{year}/{round_number}/results"
        else:
            endpoint = f"{year}/results"
            
        data = self._make_request(endpoint)
        
        if not data or 'MRData' not in data:
            return []
            
        race_table = data['MRData']['RaceTable']
        races = race_table.get('Races', [])
        
        results = []
        for race in races:
            if 'Results' in race:
                race_results = [{
                    'position': int(result['position']) if result['position'].isdigit() else None,
                    'points': float(result['points']),
                    'driver': {
                        'id': result['Driver']['driverId'],
                        'code': result['Driver'].get('code', ''),
                        'first_name': result['Driver']['givenName'],
                        'last_name': result['Driver']['familyName']
                    },
                    'constructor': {
                        'id': result['Constructor']['constructorId'],
                        'name': result['Constructor']['name']
                    },
                    'grid': int(result['grid']) if result['grid'].isdigit() else None,
                    'laps': int(result['laps']) if result['laps'].isdigit() else None,
                    'status': result['status'],
                    'time': result.get('Time', {}).get('time', ''),
                    'fastest_lap': result.get('FastestLap', {})
                } for result in race['Results']]
                
                results.append({
                    'round': int(race['round']),
                    'name': race['raceName'],
                    'date': race['date'],
                    'results': race_results
                })
        
        return results
    
    def get_drivers(self, year=None):
        """Get all drivers for the season."""
        year = year or self.CURRENT_SEASON
        data = self._make_request(f"{year}/drivers")
        
        if not data or 'MRData' not in data:
            return []
            
        drivers = data['MRData']['DriverTable']['Drivers']
        
        return [{
            'id': driver['driverId'],
            'code': driver.get('code', ''),
            'number': driver.get('permanentNumber', ''),
            'first_name': driver['givenName'],
            'last_name': driver['familyName'],
            'nationality': driver['nationality'],
            'date_of_birth': driver['dateOfBirth'],
            'url': driver['url']
        } for driver in drivers]
    
    def get_constructors(self, year=None):
        """Get all constructors for the season."""
        year = year or self.CURRENT_SEASON
        data = self._make_request(f"{year}/constructors")
        
        if not data or 'MRData' not in data:
            return []
            
        constructors = data['MRData']['ConstructorTable']['Constructors']
        
        return [{
            'id': constructor['constructorId'],
            'name': constructor['name'],
            'nationality': constructor['nationality'],
            'url': constructor['url']
        } for constructor in constructors]
    
    def get_qualifying_results(self, year=None, round_number=None):
        """Get qualifying results."""
        year = year or self.CURRENT_SEASON
        
        if round_number:
            endpoint = f"{year}/{round_number}/qualifying"
        else:
            endpoint = f"{year}/qualifying"
            
        data = self._make_request(endpoint)
        
        if not data or 'MRData' not in data:
            return []
            
        races = data['MRData']['RaceTable']['Races']
        
        results = []
        for race in races:
            if 'QualifyingResults' in race:
                qualifying_results = [{
                    'position': int(result['position']),
                    'driver': {
                        'id': result['Driver']['driverId'],
                        'code': result['Driver'].get('code', ''),
                        'first_name': result['Driver']['givenName'],
                        'last_name': result['Driver']['familyName']
                    },
                    'constructor': {
                        'id': result['Constructor']['constructorId'],
                        'name': result['Constructor']['name']
                    },
                    'q1': result.get('Q1', ''),
                    'q2': result.get('Q2', ''),
                    'q3': result.get('Q3', '')
                } for result in race['QualifyingResults']]
                
                results.append({
                    'round': int(race['round']),
                    'name': race['raceName'],
                    'date': race['date'],
                    'qualifying_results': qualifying_results
                })
        
        return results


class RacingService:
    """Service for internal racing data logic and OpenF1 integration."""
    
    @staticmethod
    def get_session_info(year, round_number, session_type='RACE'):
        """Retrieve local session info including OpenF1 keys."""
        from apps.racing.models import Session
        try:
            return Session.objects.filter(
                race__season__year=year,
                race__round_number=round_number,
                session_type=session_type
            ).first()
        except Exception as e:
            logger.error(f"Error fetching local session: {e}")
            return None

    @staticmethod
    def enrich_race_with_telemetry(race_data):
        """Inject OpenF1 session keys into race data dictionaries."""
        try:
            year = int(race_data['date'][:4])
            round_num = race_data['round']
            
            session = RacingService.get_session_info(year, round_num)
            if session:
                race_data['openf1_session_key'] = session.openf1_session_key
                race_data['status'] = session.status
        except (ValueError, KeyError, TypeError):
            pass
        return race_data


# Singleton instances
ergast_service = ErgastF1Service()
racing_service = RacingService()
