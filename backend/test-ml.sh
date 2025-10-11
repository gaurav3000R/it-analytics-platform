#!/bin/bash

# ML Model Testing Script
# =======================
# Run this script to test your trained ML model

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🧪 ML Model Testing                                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Run: uv sync${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✓ Activating virtual environment...${NC}"
source .venv/bin/activate

# Test 1: Python Module Tests
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 1: Python Module Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python app/test_ml.py

# Test 2: API Tests (if server is running)
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Test 2: API Endpoint Tests${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}To test API endpoints:${NC}"
echo -e "  1. Start the server in another terminal:"
echo -e "     ${GREEN}uvicorn app.main:app --reload${NC}"
echo -e "  2. Run: ${GREEN}python app/test_ml.py --api${NC}"
echo ""

# Test 3: Quick curl tests (if server is running)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Test 3: Quick API Tests with curl${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if server is running
if curl -s http://localhost:8000/ml/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running!${NC}"
    echo ""
    
    echo "1. Health Check:"
    curl -s http://localhost:8000/ml/health | python -m json.tool
    echo ""
    
    echo "2. Model Info:"
    curl -s http://localhost:8000/ml/model/info | python -m json.tool
    echo ""
    
    echo "3. Sample Prediction:"
    curl -s -X POST http://localhost:8000/ml/predict \
         -H "Content-Type: application/json" \
         -d '{
             "agile_effectiveness": 5,
             "risk_mitigation": 4,
             "management_satisfaction": 5,
             "supply_chain_improvement": 4,
             "time_efficiency": 4,
             "cost_savings_pct": 30
         }' | python -m json.tool
    echo ""
    
    echo -e "${GREEN}✅ API tests completed!${NC}"
else
    echo -e "${YELLOW}ℹ️  Server not running on localhost:8000${NC}"
    echo ""
    echo "To start the server:"
    echo -e "  ${GREEN}uvicorn app.main:app --reload${NC}"
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Testing Complete!                                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
