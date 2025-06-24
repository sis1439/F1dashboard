import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def format_lap_time(time_obj) -> Optional[str]:
    """
    Format lap time to mm:ss.sss format
    
    Args:
        time_obj: Time object (timedelta, float, or None)
        
    Returns:
        Formatted time string or None if invalid
    """
    if pd.isna(time_obj) or time_obj is None:
        return None
    
    try:
        if hasattr(time_obj, 'total_seconds'):
            total_seconds = time_obj.total_seconds()
        else:
            total_seconds = float(time_obj)
        
        if total_seconds <= 0:
            return None
            
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"
    except Exception as e:
        logger.error(f"Error formatting lap time: {e}")
        return None


def format_race_time(time_obj) -> Optional[str]:
    """
    Format race time to h:mm:ss.sss format, removing day component
    
    Args:
        time_obj: Time object (timedelta, float, or None)
        
    Returns:
        Formatted time string or None if invalid
    """
    if pd.isna(time_obj) or time_obj is None:
        return None
    
    try:
        if hasattr(time_obj, 'total_seconds'):
            total_seconds = time_obj.total_seconds()
        elif hasattr(time_obj, 'days') and hasattr(time_obj, 'seconds'):
            # Handle timedelta objects with days, only take time components
            total_seconds = time_obj.seconds + time_obj.microseconds / 1000000
        else:
            total_seconds = float(time_obj)
        
        if total_seconds <= 0:
            return None
            
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:06.3f}"
        else:
            return f"{minutes:02d}:{seconds:06.3f}"
    except Exception as e:
        logger.error(f"Error formatting race time: {e}")
        return None


def format_gap_time(gap_seconds: float) -> str:
    """
    Format gap time to +X.XXXs format
    
    Args:
        gap_seconds: Gap in seconds
        
    Returns:
        Formatted gap string
    """
    try:
        if gap_seconds <= 0:
            return ""
        return f"+{gap_seconds:.3f}s"
    except Exception as e:
        logger.error(f"Error formatting gap time: {e}")
        return ""


def calculate_session_status(session_datetime, end_datetime, current_time=None):
    """
    Calculate session status based on current time
    
    Args:
        session_datetime: Session start datetime
        end_datetime: Session end datetime
        current_time: Current time (defaults to now)
        
    Returns:
        Status string: "upcoming", "live", or "completed"
    """
    if current_time is None:
        current_time = pd.Timestamp.now()
    
    try:
        # Handle timezone conversion if needed
        if hasattr(session_datetime, 'tz') and session_datetime.tz is not None:
            current_time = pd.Timestamp.now(tz='UTC')
            session_utc = session_datetime.tz_convert('UTC')
            end_utc = end_datetime.tz_convert('UTC')
            
            if current_time > end_utc:
                return "completed"
            elif current_time >= session_utc:
                return "live"
            else:
                return "upcoming"
        else:
            # No timezone info, use local time
            if current_time > end_datetime:
                return "completed"
            elif current_time >= session_datetime:
                return "live"
            else:
                return "upcoming"
                
    except Exception as e:
        logger.error(f"Error calculating session status: {e}")
        return "upcoming"  # Default to upcoming on error 