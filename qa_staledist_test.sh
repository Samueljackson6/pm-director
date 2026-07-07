#!/usr/bin/env bash
# QA test harness for T2 stale-dist guard (mirrors deploy-docker.sh lines 97-108)
set -uo pipefail

# ---- Faithful replica of the guard logic in scripts/deploy-docker.sh ----
guard_check() {
  local DIST_INDEX="$1"
  local BUILD_START_TS="$2"
  if [ ! -f "$DIST_INDEX" ]; then
    echo "  [guard] FAIL: 构建产物缺失: $DIST_INDEX（build 未产出，中止部署）"
    return 1
  fi
  local DIST_MTIME
  DIST_MTIME=$(date -r "$DIST_INDEX" +%s 2>/dev/null || stat -c %Y "$DIST_INDEX" 2>/dev/null || echo 0)
  if [ "$DIST_MTIME" -lt "$BUILD_START_TS" ]; then
    echo "  [guard] FAIL: 构建产物不新鲜 (stale-dist)：dist/index.html 早于 build 开始时间，中止部署"
    return 1
  fi
  echo "  [guard] PASS: 前端产物校验通过: $DIST_INDEX"
  return 0
}

ART=/tmp/qa_art
rm -rf "$ART"
mkdir -p "$ART/dist"
DIST_INDEX="$ART/dist/index.html"

BUILD_START_TS=$(date +%s)
sleep 1   # simulate build taking a moment

echo "=============================================="
echo "Scenario 1: dist/index.html 存在且 mtime >= BUILD_START_TS"
echo "=============================================="
: > "$DIST_INDEX"
touch "$DIST_INDEX"
guard_check "$DIST_INDEX" "$BUILD_START_TS"
RC1=$?
echo "  -> exit code = $RC1 (expect 0 = PASS)"

echo ""
echo "=============================================="
echo "Scenario 2: dist/index.html 缺失（模拟 build 未产出）"
echo "=============================================="
rm -f "$DIST_INDEX"
guard_check "$DIST_INDEX" "$BUILD_START_TS"
RC2=$?
echo "  -> exit code = $RC2 (expect 1 = FAIL, 部署中止)"

echo ""
echo "=============================================="
echo "Scenario 3: dist/index.html mtime 早于 BUILD_START_TS（模拟 stale-dist）"
echo "=============================================="
: > "$DIST_INDEX"
touch -d "$(date -d @$((BUILD_START_TS - 60)) '+%Y-%m-%d %H:%M:%S')" "$DIST_INDEX"
echo "  BUILD_START_TS=$BUILD_START_TS  DIST_MTIME=$(date -r "$DIST_INDEX" +%s)"
guard_check "$DIST_INDEX" "$BUILD_START_TS"
RC3=$?
echo "  -> exit code = $RC3 (expect 1 = FAIL, stale-dist 被拦截)"

echo ""
echo "=============================================="
echo "RESULT SUMMARY"
echo "=============================================="
echo "Scenario1 (fresh)   : rc=$RC1 (want 0)"
echo "Scenario2 (missing) : rc=$RC2 (want 1)"
echo "Scenario3 (stale)   : rc=$RC3 (want 1)"

if [ "$RC1" -eq 0 ] && [ "$RC2" -eq 1 ] && [ "$RC3" -eq 1 ]; then
  echo "OVERALL: GUARD LOGIC CORRECT"
  exit 0
else
  echo "OVERALL: GUARD LOGIC INCORRECT"
  exit 1
fi
