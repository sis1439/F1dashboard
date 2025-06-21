# F1 Dashboard

*Real-time Formula 1 analytics, from qualifying laps to championship standings.*

---

## Project at a Glance

F1 Dashboard is a full-stack application that ingests official Formula 1 timing data and serves a responsive, single-page dashboard. The project explores the intersection of data engineering (streaming & caching), API design and modern front-end development.

---

## Key Highlights

• **FastAPI & Python 3.10** – asynchronous endpoints with automatic OpenAPI docs.  
• **React + TypeScript** – component-driven UI, state isolated via hooks and context.  
• **Redis caching** – race results are cached for sub-100 ms repeated responses.  
• **CI-ready** – pytest & React Testing Library tests included.  
• **Docker friendly** – optional `docker-compose` stack for one-command spin-up (coming soon).

---

## Quick Start (Local)

### 1. Clone & Install
```bash
git clone https://github.com/your-username/F1-dashboard.git
cd F1-dashboard
```

### 2. Back-end
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```
Visit <http://localhost:8000/docs> for interactive API docs.

### 3. Front-end
```bash
cd my-app
npm install
npm start
```
Open <http://localhost:3000> in your browser.

### 4. Optional: Redis
The API will fall back to in-memory caching if Redis is absent, but running a local Redis instance is recommended:
```bash
brew install redis  # macOS
redis-server
```

---

## Folder Structure
```text
F1-dashboard/
├─ backend/      # FastAPI service
│  ├─ main.py
│  ├─ schedule_api.py | standings_api.py | race_results_api.py
│  └─ cache_utils.py
├─ my-app/       # React client (CRA)
│  └─ src/
└─ tests/        # unit & integration tests
```

---

## What I Focused On

1. **Performance** – A cold call to the Ergast/FastF1 sources can take seconds; Redis cuts subsequent calls to milliseconds.
2. **ETL & Data Enrichment** – Raw telemetry and API responses are extracted, normalized into analytics-friendly schemas, enriched with circuit metadata, and loaded into Redis before being served to the client.
3. **Maintainability** – Clear module boundaries and type annotations across the stack.
4. **Testability** – Business logic is decoupled from transport, enabling pytest isolation; front-end follows Jest conventions.

---

## License

MIT © 2024 <https://github.com/sis1439> 