#!/bin/bash
# ==============================================
# Fashion Forecast Backend - Development Server
# ==============================================
# Start the FastAPI backend with auto-reload enabled
#
# Usage:
#   ./backend/scripts/dev.sh
#
# Features:
#   - Auto-reload on code changes
#   - Detailed error logging
#   - CORS enabled for frontend development
#   - Runs on http://0.0.0.0:8000

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Fashion Forecast Backend - Dev Server${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if we're in the correct directory
if [ ! -f "backend/app/main.py" ]; then
    echo -e "${YELLOW}⚠ Warning: Run this script from the project root directory${NC}"
    echo -e "${YELLOW}  Example: ./backend/scripts/dev.sh${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠ Warning: backend/.env not found${NC}"
    echo -e "${YELLOW}  Copying .env.example to .env...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env${NC}"
    echo -e "${YELLOW}  Please edit .env with your Azure OpenAI credentials${NC}"
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ] && [ ! -d "backend/.venv" ] && [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠ Warning: No virtual environment detected${NC}"
    echo -e "${YELLOW}  Create one with: python -m venv backend/venv${NC}"
    echo -e "${YELLOW}  Activate it with: source backend/venv/bin/activate${NC}"
    echo ""
fi

# Navigate to backend directory
cd backend

echo -e "${GREEN}Starting development server...${NC}"
echo -e "${BLUE}📍 URL: http://localhost:8000${NC}"
echo -e "${BLUE}📚 API Docs: http://localhost:8000/docs${NC}"
echo -e "${BLUE}🔍 Health Check: http://localhost:8000/api/v1/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start uvicorn with auto-reload
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
