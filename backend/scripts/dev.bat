@echo off
REM ==============================================
REM Fashion Forecast Backend - Development Server
REM ==============================================
REM Start the FastAPI backend with auto-reload enabled
REM
REM Usage:
REM   backend\scripts\dev.bat
REM
REM Features:
REM   - Auto-reload on code changes
REM   - Detailed error logging
REM   - CORS enabled for frontend development
REM   - Runs on http://0.0.0.0:8000

echo ========================================
echo Fashion Forecast Backend - Dev Server
echo ========================================

REM Check if we're in the correct directory
if not exist "backend\app\main.py" (
    echo [WARNING] Run this script from the project root directory
    echo   Example: backend\scripts\dev.bat
    exit /b 1
)

REM Check if .env exists
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found
    echo   Copying .env.example to .env...
    copy backend\.env.example backend\.env
    echo [SUCCESS] Created backend\.env
    echo   Please edit .env with your Azure OpenAI credentials
)

REM Check if virtual environment exists
if not exist "backend\venv" (
    if not exist "backend\.venv" (
        if not exist "venv" (
            if not exist ".venv" (
                echo [WARNING] No virtual environment detected
                echo   Create one with: python -m venv backend\venv
                echo   Activate it with: backend\venv\Scripts\activate
                echo.
            )
        )
    )
)

REM Navigate to backend directory
cd backend

echo Starting development server...
echo - URL: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/api/v1/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start uvicorn with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
