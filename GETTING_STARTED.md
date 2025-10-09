# IT Analytics Platform - Complete Getting Started Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.13+
- Node.js 20+
- Git

### Step 1: Start Backend (2 minutes)
```bash
cd backend
uv sync
npm run dev
```
✅ Backend running on http://localhost:8000

### Step 2: Start Frontend (2 minutes)
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
✅ Frontend running on http://localhost:3000

### Step 3: Access Application
Open http://localhost:3000 in your browser

---

## 📋 Detailed Setup Instructions

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd /path/to/it-analytics-platform/backend
```

#### 2. Install Dependencies
The backend uses `uv` for Python dependency management:
```bash
uv sync
```

#### 3. Configure Environment
The `.env` file is already configured with defaults:
```env
DATABASE_URL=sqlite:///./it_analytics.db
SECRET_KEY=dev-secret-key-change-in-production
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
GOOGLE_API_KEY=  # Optional - for AI features
```

#### 4. Start Backend Server
```bash
npm run dev
# or
uv run uvicorn app.main:app --reload
```

#### 5. Verify Backend
Open http://localhost:8000/docs to see API documentation

---

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd /path/to/it-analytics-platform/frontend
```

#### 2. Install Dependencies
```bash
npm install --legacy-peer-deps
```

#### 3. Configure Environment (Optional)
Create `.env.local` if needed:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### 4. Start Frontend Server
```bash
npm run dev
```

#### 5. Verify Frontend
Open http://localhost:3000 to see the dashboard

---

## 🎯 First-Time Usage

### 1. Load Sample Data
Once both servers are running:

**Option A: Via API**
```bash
curl -X POST http://localhost:8000/api/v1/projects/load-default-csv
```

**Option B: Via Frontend**
- Navigate to Projects page
- Click "Load Sample Data"
- Wait for data to load

### 2. Explore Dashboard
- View real-time project metrics
- Check risk distribution
- Review recent alerts
- Browse projects table

### 3. Enable AI Features (Optional)
1. Get Google Gemini API key from https://makersuite.google.com/app/apikey
2. Add to `backend/.env`:
   ```env
   GOOGLE_API_KEY=your-actual-api-key-here
   ```
3. Restart backend server
4. Access AI Insights from sidebar

---

## 🔧 Troubleshooting

### Backend Issues

#### Port 8000 Already in Use
```bash
lsof -ti:8000 | xargs kill -9
```

#### Database Not Found
```bash
cd backend
# Database will be created automatically on first run
```

#### Import Errors
```bash
cd backend
uv sync --reinstall
```

### Frontend Issues

#### Port 3000 Already in Use
```bash
lsof -ti:3000 | xargs kill -9
```

#### Module Not Found
```bash
cd frontend
rm -rf .next node_modules
npm install --legacy-peer-deps
```

#### API Connection Failed
- Check backend is running: `curl http://localhost:8000`
- Verify CORS settings in backend
- Check browser console for errors

---

## 📊 API Endpoints Reference

### Health Check
```bash
curl http://localhost:8000/
```

### Analytics Overview
```bash
curl http://localhost:8000/api/v1/analytics/overview
```

### Risk Dashboard
```bash
curl http://localhost:8000/api/v1/analytics/risk-dashboard
```

### All Projects
```bash
curl http://localhost:8000/api/v1/projects/
```

---

## 🎨 Features Overview

### Dashboard Features
- **Real-time Metrics**: Live project statistics
- **Risk Analysis**: Visual risk distribution
- **System Status**: Component health indicators
- **Recent Alerts**: Latest anomaly notifications
- **Project Table**: Searchable and filterable list

### Available Modules
1. **Projects** - Project management and tracking
2. **Risk Analysis** - ML-powered risk prediction
3. **AI Insights** - Gemini AI analysis (with API key)
4. **Bug Tracker** - Bug analysis and tracking
5. **Resources** - Team utilization monitoring
6. **Cost Forecasting** - Budget analysis
7. **Analytics** - Comprehensive dashboards

---

## 🔐 Security Notes

### Development Environment
Current setup uses:
- Default SECRET_KEY (change in production)
- SQLite database (switch to PostgreSQL for production)
- No authentication (implement for production)

### Production Checklist
- [ ] Change SECRET_KEY to strong random value
- [ ] Use PostgreSQL or MySQL database
- [ ] Implement authentication (JWT tokens)
- [ ] Enable HTTPS
- [ ] Set up proper CORS origins
- [ ] Configure environment variables properly
- [ ] Add rate limiting
- [ ] Enable security headers

---

## 📦 Project Structure

```
it-analytics-platform/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities
│   ├── pyproject.toml         # Python dependencies
│   └── .env                   # Environment config
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Pages & layouts
│   │   ├── components/        # React components
│   │   ├── services/          # API clients
│   │   ├── lib/               # Utilities
│   │   └── types/             # TypeScript types
│   └── package.json           # Node dependencies
│
└── docs/                       # Documentation
```

---

## 🚀 Development Workflow

### Making Changes

#### Backend Changes
1. Edit Python files in `backend/app/`
2. Server auto-reloads with changes
3. Test at http://localhost:8000/docs

#### Frontend Changes
1. Edit React components in `frontend/src/`
2. Hot reload updates browser automatically
3. View at http://localhost:3000

### Adding New Features

#### New Backend Endpoint
1. Create route in `backend/app/api/`
2. Define model if needed
3. Add business logic in services
4. Test with Swagger UI

#### New Frontend Component
1. Create component in appropriate directory
2. Add types in `types/index.ts`
3. Create API function in `services/api.ts`
4. Use React Query for data fetching

---

## 📖 Documentation Links

- **Frontend Docs**: `FRONTEND_DOCUMENTATION.md`
- **Frontend Summary**: `FRONTEND_IMPLEMENTATION_SUMMARY.md`
- **Backend Fixes**: `backend/DEPENDENCY_FIXES.md`
- **Backend Summary**: `backend/CLEANUP_SUMMARY.txt`

---

## 🎓 Technology Stack

### Backend
- **Framework**: FastAPI 0.116.1+
- **Database**: SQLAlchemy 2.0+ with SQLite/PostgreSQL
- **ML**: scikit-learn 1.7+
- **AI**: Google Gemini AI
- **Package Manager**: uv

### Frontend
- **Framework**: Next.js 15.5.2
- **UI Library**: React 19.1.0
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **State**: React Query + Zustand
- **Animation**: Framer Motion

---

## 💡 Tips & Best Practices

### Development Tips
1. Keep both servers running during development
2. Use browser DevTools for debugging
3. Check backend logs for API errors
4. Use React DevTools for component inspection

### Performance Tips
1. Enable React Query cache
2. Use code splitting for large components
3. Optimize images before uploading
4. Monitor network requests

### Code Quality
1. Run ESLint regularly: `npm run lint`
2. Follow TypeScript strict mode
3. Add comments for complex logic
4. Keep components small and focused

---

## 🆘 Getting Help

### Common Resources
1. Backend API Docs: http://localhost:8000/docs
2. Frontend README: `frontend/README.md`
3. Backend Config: `backend/pyproject.toml`
4. Frontend Config: `frontend/package.json`

### Debug Checklist
- [ ] Both servers running?
- [ ] Correct ports (8000, 3000)?
- [ ] Environment variables set?
- [ ] Dependencies installed?
- [ ] Check browser console
- [ ] Check server logs

---

## 📝 Next Steps

Once you have the application running:

1. **Explore Features**: Navigate through all modules
2. **Load Data**: Upload CSV or generate sample data
3. **Customize**: Modify components to your needs
4. **Add Features**: Extend with new endpoints
5. **Deploy**: Prepare for production deployment

---

## 🎉 Success Indicators

You're ready when you see:
- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000
- ✅ Dashboard loading without errors
- ✅ Sample data visible in tables
- ✅ Charts rendering correctly
- ✅ No console errors

---

**Happy Coding! 🚀**

For detailed documentation, see the respective documentation files for backend and frontend.
