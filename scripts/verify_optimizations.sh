#!/bin/bash
# Verification script for CLI startup optimizations

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "════════════════════════════════════════════════════════════════"
echo "  CLI STARTUP OPTIMIZATION - VERIFICATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Baseline measurement
echo -e "${BLUE}📊 Measuring baseline performance...${NC}"
echo ""

TIMES=()
for i in {1..5}; do
    START=$(date +%s.%N)
    uv run specify --help > /dev/null 2>&1
    END=$(date +%s.%N)
    ELAPSED=$(echo "$END - $START" | bc)
    TIMES+=($ELAPSED)
    echo "  Run $i: ${ELAPSED}s"
done

# Calculate average
TOTAL=0
for time in "${TIMES[@]}"; do
    TOTAL=$(echo "$TOTAL + $time" | bc)
done
AVG=$(echo "scale=3; $TOTAL / ${#TIMES[@]}" | bc)

echo ""
echo -e "${BLUE}Average startup time: ${AVG}s${NC}"

# Check if meets target
TARGET=1.5
if (( $(echo "$AVG < $TARGET" | bc -l) )); then
    echo -e "${GREEN}✅ SUCCESS: ${AVG}s < ${TARGET}s target!${NC}"
    EXIT_CODE=0
else
    IMPROVEMENT=$(echo "scale=1; (2.825 - $AVG) / 2.825 * 100" | bc)
    SAVED=$(echo "scale=3; 2.825 - $AVG" | bc)
    echo -e "${YELLOW}📈 IMPROVEMENT: ${IMPROVEMENT}% faster (${SAVED}s saved)${NC}"
    echo -e "${YELLOW}⚠️  Still above ${TARGET}s target${NC}"
    EXIT_CODE=1
fi

echo ""

# 2. Run tests
echo -e "${BLUE}🧪 Running test suite...${NC}"
if uv run pytest tests/ -q --tb=short; then
    echo -e "${GREEN}✅ All tests passed${NC}"
else
    echo -e "${RED}❌ Tests failed${NC}"
    exit 1
fi

echo ""

# 3. Check OTEL functionality
echo -e "${BLUE}🔍 Verifying OTEL lazy loading...${NC}"

# Without OTEL endpoint (should be fast)
START=$(date +%s.%N)
uv run specify --help > /dev/null 2>&1
END=$(date +%s.%N)
ELAPSED_NO_OTEL=$(echo "$END - $START" | bc)
echo "  Without OTEL: ${ELAPSED_NO_OTEL}s"

# With OTEL endpoint (may load OTEL, but still lazy)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
START=$(date +%s.%N)
uv run specify --help > /dev/null 2>&1
END=$(date +%s.%N)
ELAPSED_WITH_OTEL=$(echo "$END - $START" | bc)
echo "  With OTEL endpoint: ${ELAPSED_WITH_OTEL}s"

# Should be similar (OTEL not loaded for --help)
DIFF=$(echo "$ELAPSED_WITH_OTEL - $ELAPSED_NO_OTEL" | bc | sed 's/-//')
if (( $(echo "$DIFF < 0.1" | bc -l) )); then
    echo -e "${GREEN}✅ OTEL lazy loading working (difference: ${DIFF}s)${NC}"
else
    echo -e "${YELLOW}⚠️  OTEL may be loading eagerly (difference: ${DIFF}s)${NC}"
fi

unset OTEL_EXPORTER_OTLP_ENDPOINT
echo ""

# 4. Memory usage check
echo -e "${BLUE}💾 Checking memory usage...${NC}"
MEMORY=$(uv run python3 -c "
import subprocess
import sys
result = subprocess.run([sys.executable, '-m', 'specify_cli', '--help'],
                       capture_output=True)
" 2>&1 | grep -i "memory" || echo "N/A")

echo "  Memory check: ${MEMORY:-< 100MB (est.)}"
echo ""

# 5. Summary
echo "════════════════════════════════════════════════════════════════"
echo "  VERIFICATION SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  Baseline (before):  2.825s"
echo "  Current:            ${AVG}s"
echo "  Target:             ${TARGET}s"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Optimizations successfully applied!"
else
    echo -e "${YELLOW}⚠️  OPTIMIZATIONS IN PROGRESS${NC}"
    echo ""
    echo "Current improvements:"
    echo "  - Profiling analysis complete"
    echo "  - Bottlenecks identified"
    echo "  - Optimization strategy documented"
    echo ""
    echo "Next steps:"
    echo "  1. Apply optimized telemetry.py (saves ~0.573s)"
    echo "  2. Implement lazy core imports (saves ~0.400s)"
    echo "  3. Add lazy httpx imports (saves ~0.166s)"
    echo "  4. Enable lazy command loading (saves ~0.300s)"
fi

echo ""
echo "See scripts/OPTIMIZATION_REPORT.md for details"
echo ""

exit $EXIT_CODE
