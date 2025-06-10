import pytest
from fastapi.testclient import TestClient
from main import app
import fastf1
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def mock_fastf1():
    with patch('fastf1.get_event_schedule') as mock_schedule, \
         patch('fastf1.get_event') as mock_event:
        
        # Mock schedule data
        mock_schedule_data = pd.DataFrame({
            'EventName': ['Abu Dhabi'],
            'RoundNumber': [1]
        })
        mock_schedule.return_value = mock_schedule_data
        
        # Mock session data
        mock_session = MagicMock()
        mock_standings = pd.DataFrame({
            'Position': [1, 2, 3],
            'Full Name': ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc'],
            'Points': [454.0, 387.0, 308.0]
        })
        mock_session.get_driver_standings.return_value = mock_standings
        mock_event.return_value = mock_session
        
        yield mock_schedule, mock_event

def test_driver_standings_default_year(mock_fastf1):
    response = client.get("/api/driver-standings")
    assert response.status_code == 200
    data = response.json()
    
    # Check if we got the expected number of drivers
    assert len(data) == 3
    
    # Check the structure of the response
    first_driver = data[0]
    assert "pos" in first_driver
    assert "name" in first_driver
    assert "points" in first_driver
    assert "evo" in first_driver
    
    # Check specific values
    assert first_driver["pos"] == 1
    assert first_driver["name"] == "Max Verstappen"
    assert first_driver["points"] == 454.0
    assert first_driver["evo"] == 0

def test_driver_standings_specific_year(mock_fastf1):
    response = client.get("/api/driver-standings?year=2023")
    assert response.status_code == 200
    data = response.json()
    
    # Check if we got the expected number of drivers
    assert len(data) == 3
    
    # Check the structure of the response
    first_driver = data[0]
    assert "pos" in first_driver
    assert "name" in first_driver
    assert "points" in first_driver
    assert "evo" in first_driver
    
    # Check specific values
    assert first_driver["pos"] == 1
    assert first_driver["name"] == "Max Verstappen"
    assert first_driver["points"] == 454.0
    assert first_driver["evo"] == 0

def test_available_years():
    response = client.get("/api/available-years")
    assert response.status_code == 200
    years = response.json()
    
    # 验证年份列表的基本属性
    assert isinstance(years, list)
    assert len(years) > 0
    
    # 验证年份范围
    current_year = datetime.now().year
    assert min(years) == 1950  # F1开始年份
    assert max(years) == current_year
    
    # 验证年份是连续的
    assert years == list(range(1950, current_year + 1)) 