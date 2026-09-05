#!/bin/bash

# PulseWatch Startup Script
echo "=================================================="
echo "⚡ Starting PulseWatch Market Intelligence Terminal"
echo "=================================================="

BACKEND_DIR="/Users/magicpin/pulsewatch/backend"
FRONTEND_DIR="/Users/magicpin/pulsewatch/frontend"

# 1. Start Backend FastAPI Server
echo "🚀 Launching FastAPI Backend on http://localhost:8000 ..."
cd "$BACKEND_DIR"
PYTHONPATH="$BACKEND_DIR" "$BACKEND_DIR/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Frontend Vite Dev Server
echo "✨ Launching React Terminal Frontend on http://localhost:3000 ..."
cd "$FRONTEND_DIR"
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "🛑 Shutting down PulseWatch..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "✅ PulseWatch Terminal is LIVE!"
echo "👉 Frontend: http://localhost:3000"
echo "👉 Backend API Docs: http://localhost:8000/docs"
echo "👉 WebSocket Live Stream: ws://localhost:8000/ws"
echo "=================================================="

wait
