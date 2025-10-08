#!/bin/bash

# IT Analytics Platform - Development Startup Script
# This script starts both frontend and backend servers concurrently

set -e

echo "🚀 Starting IT Analytics Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the root directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}Port $1 is already in use. Please stop the existing process.${NC}"
        exit 1
    fi
}

# Check if ports are available
echo "Checking ports..."
check_port 3000
check_port 8000
echo -e "${GREEN}✓ Ports 3000 and 8000 are available${NC}"
echo ""

# Check if backend virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✓ Backend environment created${NC}"
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
fi

# Initialize database if it doesn't exist
if [ ! -f "backend/it_analytics.db" ]; then
    echo -e "${BLUE}Initializing database with sample data...${NC}"
    cd backend
    source .venv/bin/activate
    python app/main.py --setup-data
    python app/main.py --train-models
    cd ..
    echo -e "${GREEN}✓ Database initialized${NC}"
    echo ""
fi

echo -e "${GREEN}Starting servers...${NC}"
echo ""
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}Stopping servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start backend server
cd backend
source .venv/bin/activate
uvicorn app.handler:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend server
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID