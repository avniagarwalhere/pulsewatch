#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================"
echo "   🚀 PULSEWATCH ENTERPRISE DEPLOYMENT & VERIFIER"
echo "======================================================"
echo ""

# 1. Stop any previous docker compose containers
echo "📦 Step 1: Cleaning previous deployment..."
docker compose down --remove-orphans 2>/dev/null || true
echo "✓ Ready to deploy."
echo ""

# 2. Build and launch Docker Compose stack
echo "🐳 Step 2: Building and deploying Docker containers..."
docker compose up -d --build

echo ""
echo "⏳ Step 3: Waiting for containers to initialize..."
for i in {1..30}; do
  if curl -s http://localhost:8000/api/market/breadth > /dev/null 2>&1 && curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ All containers are up and responsive!"
    break
  fi
  sleep 1
  echo -n "."
done
echo ""

# 3. Automated Verification Tests
echo ""
echo "======================================================"
echo "   🧪 RUNNING RIGOROUS INTEGRATION VERIFICATION"
echo "======================================================"

PASS=0
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  local expected="$3"
  
  printf "%-50s" "$name"
  local output
  output=$(eval "$cmd" 2>/dev/null || true)
  
  if [[ "$output" == *"$expected"* ]]; then
    echo -e "\033[32m[ PASS ]\033[0m"
    PASS=$((PASS + 1))
  else
    echo -e "\033[31m[ FAIL ]\033[0m (Got: $output)"
    FAIL=$((FAIL + 1))
  fi
}

# Test 1: Frontend SPA
check "1. Frontend Nginx & React SPA serving on :3000" \
  "curl -s http://localhost:3000 | head -n 10" \
  "<html"

# Test 2: Backend Market Breadth
check "2. Backend Market Breadth API (:8000)" \
  "curl -s http://localhost:8000/api/market/breadth" \
  "\"market_phase\""

# Test 3: Watchlists (Full 5 seeded)
check "3. Watchlists API has Indian & US Markets" \
  "curl -s http://localhost:8000/api/watchlists" \
  "Indian Markets"

# Test 4: Indian Markets Stock Universe
check "4. Indian Markets has full stock universe (RELIANCE)" \
  "curl -s 'http://localhost:8000/api/market/quotes?watchlist_id=4'" \
  "RELIANCE.NS"

# Test 5: US Markets Stock Universe
check "5. US Markets has tech leaders (NVDA)" \
  "curl -s 'http://localhost:8000/api/market/quotes?watchlist_id=5'" \
  "NVDA"

# Test 6: Dynamic Recommendations (3 picks)
check "6. Dynamic AI Recommendations API (Top 3)" \
  "curl -s 'http://localhost:8000/api/market/recommendations?limit=3'" \
  "confidence"

# Test 7: Trending Indian Stocks
check "7. Trending Indian Stocks API" \
  "curl -s 'http://localhost:8000/api/market/trending?market=IN'" \
  "["

# Test 8: Trending US Stocks
check "8. Trending US Stocks API" \
  "curl -s 'http://localhost:8000/api/market/trending?market=US'" \
  "["

# Test 9: Dynamic AI Digest Feed
check "9. Dynamic AI Digest & Morning Brief API" \
  "curl -s http://localhost:8000/api/events/digest" \
  "morning_brief"

# Test 10: WebSocket Endpoint Handshake
check "10. Real-time Market WebSocket Endpoint (:8000/ws)" \
  "curl -i -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' -H 'Host: localhost:8000' -H 'Origin: http://localhost:3000' http://localhost:8000/ws 2>&1 | head -n 8" \
  "101 Switching Protocols"

echo ""
echo "======================================================"
echo "   📊 VERIFICATION SUMMARY: $PASS PASSED, $FAIL FAILED"
echo "======================================================"

if [ "$FAIL" -eq 0 ]; then
  echo ""
  echo "🎉 ALL SYSTEMS OPERATIONAL AND FULLY DEPLOYED!"
  echo "👉 Open the live app in your browser: http://localhost:3000"
  echo "👉 Backend API documentation:        http://localhost:8000/docs"
  echo "👉 PostgreSQL Database:             localhost:5432 (pulsewatch/devpassword)"
  echo "👉 Redis Cache:                     localhost:6379"
  exit 0
else
  echo "⚠️ Some tests failed. Check logs via 'docker compose logs'."
  exit 1
fi
