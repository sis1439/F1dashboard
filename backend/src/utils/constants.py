# Application constants

# Session types and their display names
SESSION_TYPES = {
    'FP1': 'Practice 1',
    'FP2': 'Practice 2', 
    'FP3': 'Practice 3',
    'SQ': 'Sprint Qualifying',
    'S': 'Sprint',
    'Q': 'Qualifying',
    'R': 'Race'
}

# Session durations in minutes
SESSION_DURATIONS = {
    'FP1': 90,  # Practice 1: 90 minutes
    'FP2': 90,  # Practice 2: 90 minutes  
    'FP3': 60,  # Practice 3: 60 minutes
    'SQ': 60,   # Sprint Qualifying: 60 minutes
    'S': 60,    # Sprint: ~60 minutes
    'Q': 60,    # Qualifying: 60 minutes
    'R': 120    # Race: ~2 hours
}

# Race statuses
RACE_STATUSES = {
    'FINISHED': 'Finished',
    'DNF': 'DNF',
    'DNS': 'DNS',
    'DSQ': 'DSQ',
    'NC': 'Not Classified',
    'RETIRED': 'Retired'
}

# Session statuses  
SESSION_STATUSES = {
    'UPCOMING': 'upcoming',
    'LIVE': 'live', 
    'COMPLETED': 'completed'
}

# F1 points system (current)
POINTS_SYSTEM = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
    6: 8, 7: 6, 8: 4, 9: 2, 10: 1
}

# Sprint points system
SPRINT_POINTS_SYSTEM = {
    1: 8, 2: 7, 3: 6, 4: 5, 5: 4,
    6: 3, 7: 2, 8: 1
}

# Fastest lap bonus points
FASTEST_LAP_POINTS = 1

# Maximum number of standings to return
MAX_STANDINGS_RESULTS = 10

# Valid year range for F1 data
MIN_F1_YEAR = 1950
CURRENT_YEAR_OFFSET = 1  # Allow next year for future races

# API timeouts
REQUEST_TIMEOUT = 10  # seconds
CACHE_DEFAULT_TTL = 3600  # 1 hour in seconds

# HTTP status codes
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

# Ergast API configuration
ERGAST_API_BASE_URL = "https://api.jolpi.ca/ergast/f1"
ERGAST_MAX_RETRIES = 3
ERGAST_RETRY_DELAY = 1  # seconds 