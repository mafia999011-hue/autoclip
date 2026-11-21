#!/bin/bash
# Money Clip — Shutdown Script

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "🛑 Stopping Money Clip Server..."

if [ -f app.pid ]; then
  PID=$(cat app.pid)
  if kill -0 $PID 2>/dev/null; then
    kill $PID 2>/dev/null
    sleep 1
    kill -9 $PID 2>/dev/null
    echo "✅ Stopped Money Clip (PID $PID)."
  fi
  rm -f app.pid
fi

# Cleanup any remaining processes on port 5000
PIDS=$(lsof -ti :5000 2>/dev/null)
if [ -n "$PIDS" ]; then
  kill -9 $PIDS 2>/dev/null
fi

pkill -f "python.*app.py" 2>/dev/null

echo "✅ Money Clip is completely stopped."
