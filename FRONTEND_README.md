# Trading Journal - Frontend Integration

## Monorepo Structure

This project now includes both a Python FastAPI backend and a Vue.js frontend in a single repository.

```
trading-journal/
├── frontend/               # Vue.js Frontend
│   ├── src/
│   │   ├── views/         # Page components
│   │   ├── services/      # API integration
│   │   ├── App.vue        # Main app component
│   │   └── main.js        # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── src/                   # Python Backend (FastAPI)
├── requirements.txt
└── start scripts...
```

## Quick Start

### Development Mode (Recommended for Development)

**Windows:**
```bash
start_dev.bat
```

**Linux/Mac:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

This starts:
- Backend API on `http://localhost:8000`
- Frontend dev server on `http://localhost:5173`
- Hot-reload enabled for both

### Production Mode (Single Integrated Server)

1. Build frontend and start backend:

**Windows:**
```bash
start_full.bat
```

**Linux/Mac:**
```bash
chmod +x start_full.sh
./start_full.sh
```

This builds the Vue.js app and serves it through FastAPI on `http://localhost:8000`

## Frontend Setup (First Time)

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Backend Changes

### API Prefix
All API endpoints now use the `/api` prefix:
- Old: `http://localhost:8000/trades/`
- New: `http://localhost:8000/api/trades/`

### CORS Configuration
Updated to allow specific origins:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (alternative)

### Static File Serving
In production mode, FastAPI serves the built Vue.js app from `frontend/dist/`

## Frontend Features

### Pages
1. **Dashboard** (`/`) - Performance analytics with key metrics
2. **Trades** (`/trades`) - View, add, and delete trades with CSV export
3. **Journal** (`/journal`) - Trading journal entries with tags
4. **Overnight Fees** (`/overnight`) - View financing fees
5. **Import** (`/import`) - Bulk import from Trading212 JSON exports

### API Integration
The frontend uses Axios to communicate with the backend. All API calls go through `src/services/api.js`.

### Styling
Built-in responsive CSS with:
- Clean card-based layout
- Color-coded P&L (green/red)
- Mobile-friendly navigation
- Professional table styling

## Development Workflow

### Option 1: Separate Servers (Hot Reload)
1. Terminal 1: `python run_api.py` (Backend)
2. Terminal 2: `cd frontend && npm run dev` (Frontend)
3. Access frontend at `http://localhost:5173`

### Option 2: Integrated (Production-like)
1. `cd frontend && npm run build`
2. `python run_api.py`
3. Access everything at `http://localhost:8000`

## Environment Variables

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api
```

Change this for production deployment.

## Deployment Considerations

1. **CORS**: Update `allow_origins` in `src/app.py` with your production domain
2. **Build**: Run `npm run build` in frontend directory
3. **Static Files**: Ensure `frontend/dist/` is included in deployment
4. **Environment**: Update `VITE_API_BASE_URL` for production API

## Technology Stack

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Vue Router 4** - Client-side routing
- **Vite** - Build tool and dev server
- **Axios** - HTTP client for API calls
- **Chart.js** - Data visualization (included for future enhancements)

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **DuckDB** - Embedded database
- **Pydantic** - Data validation

## Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API calls fail with CORS error
Check that backend is running on port 8000 and CORS is configured correctly in `src/app.py`

### Production build not loading
Ensure you ran `npm run build` and `frontend/dist/` directory exists

### Backend dependency issues
```bash
pip install -r requirements.txt
```

## API Documentation

With backend running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
