from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1
from datetime import datetime

app = FastAPI()

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/available-years")
def get_available_years():
    # 从1950年（F1开始年份）到当前年份
    current_year = datetime.now().year
    years = list(range(2023, current_year + 1))
    return years

@app.get("/api/driver-standings")
def driver_standings(year: int = None):
    # 获取当前年份
    if year is None:
        year = datetime.now().year

    # 获取赛季最后一场比赛（通常是Abu Dhabi，或用fastf1.get_event_schedule自动获取）
    schedule = fastf1.get_event_schedule(year)
    last_round = schedule.index[-1]
    last_event = schedule.loc[last_round]
    gp_name = last_event['EventName']

    # 获取该场比赛的driver standings
    session = fastf1.get_event(year, gp_name)
    standings = session.get_driver_standings()

    # 只取前十
    standings = standings.head(10)

    data = []
    for _, row in standings.iterrows():
        data.append({
            "pos": int(row['Position']),
            "name": row['Full Name'],
            "points": float(row['Points']),
            "evo": 0  # 可自定义
        })
    return data

@app.get("/api/constructor-standings")
def constructor_standings(year: int = 2023):
    session = fastf1.get_event(year, 'Abu Dhabi')
    standings = session.get_team_standings()
    data = []
    for _, row in standings.iterrows():
        data.append({
            "pos": int(row['Position']),
            "name": row['Team Name'],
            "points": float(row['Points']),
            "evo": 0
        })
    return data

# 你可以继续添加其他接口，比如 /api/dashboard
