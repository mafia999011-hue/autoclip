#!/bin/bash
# Money Clip — Turnkey Startup Script

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo " 💰 MONEY CLIP — AI VIRAL SHORTS GENERATOR"
echo "=================================================="

# 1. Clean up any stale process holding port 5000
PIDS=$(lsof -ti :5000 2>/dev/null)
if [ -n "$PIDS" ]; then
  echo "⚠️ Port 5000 is in use by PID(s): $PIDS. Freeing port..."
  kill -9 $PIDS 2>/dev/null
  sleep 1
fi

pkill -f "python.*app.py" 2>/dev/null
sleep 1

# 2. Detect Local IP Address
LAN_IP=$(ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
if [ -z "$LAN_IP" ]; then
  LAN_IP="127.0.0.1"
fi

# 3. Start server in background
echo "🚀 Launching Money Clip Engine..."
nohup python3 app.py > server.log 2>&1 &
SERVER_PID=$!
disown $SERVER_PID 2>/dev/null
echo $SERVER_PID > app.pid

# 4. Wait for server readiness
for i in {1..8}; do
  sleep 1
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/health 2>/dev/null)
  if [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "✅ Money Clip is LIVE & Client-Ready!"
    echo "--------------------------------------------------"
    echo "💻 Localhost Access : http://localhost:5000"
    echo "📱 Mobile/LAN Access: http://${LAN_IP}:5000"
    echo "--------------------------------------------------"
    echo "Logs: tail -f server.log"
    echo "Stop: ./stop.sh"
    echo "=================================================="
    exit 0
  fi
done

echo "⚠️ Server started (PID $SERVER_PID). Check server.log if connection fails."
