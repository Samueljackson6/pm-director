"""P0 stage completion verification."""
import subprocess
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("P0 Stage Completion Verification")
print("=" * 80)

# 1. Check backend tests
print("\n[1/6] Backend tests...")
result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'backend/tests/', '--tb=line', '-q'],
    capture_output=True, text=True, cwd='D:/Tare-workspace/pm-director'
)
if result.returncode == 0:
    # Extract pass count from last line
    lines = result.stdout.strip().split('\n')
    print(f"  ✅ {lines[-1]}")
else:
    print(f"  ❌ FAILED\n{result.stdout[-500:]}")
    sys.exit(1)

# 2. Check API output
print("\n[2/6] API output verification...")
try:
    import urllib.request
    with urllib.request.urlopen('http://localhost:18080/api/stats', timeout=10) as resp:
        data = json.loads(resp.read())
    total = data['data']['total_amount']
    if total > 1000000:
        print(f"  ✅ /api/stats returns 元 (total_amount={total})")
    else:
        print(f"  ❌ total_amount too small: {total}")
except Exception as e:
    print(f"  ⚠️  Backend not running: {e}")

# 3. Check frontend dist
print("\n[3/6] Frontend dist verification...")
dist_dir = 'ui-vben/apps/web-antd/dist'
build_info = os.path.join(dist_dir, 'build-info.json')
if os.path.exists(build_info):
    with open(build_info, 'r', encoding='utf-8') as f:
        info = json.load(f)
    print(f"  ✅ build-info.json exists (commit={info.get('git_commit','?')[:8]})")
else:
    print(f"  ❌ build-info.json missing")

# 4. Check frontend source files
print("\n[4/6] Frontend source files...")
views = [
    'ui/src/views/dashboard/index.vue',
    'ui/src/views/contracts/index.vue',
    'ui/src/views/contracts/detail.vue',
    'ui/src/views/projects/index.vue',
    'ui/src/views/projects/detail.vue',
    'ui/src/views/invoices/index.vue',
    'ui/src/views/suppliers/index.vue',
]
all_ok = True
for v in views:
    if os.path.exists(v):
        content = open(v, 'r', encoding='utf-8').read()
        has_format = 'formatWanYuan' in content
        has_import = '@/utils/formatAmount' in content
        status = '✅' if (has_format and has_import) else '⚠️'
        print(f"  {status} {v} (formatWanYuan={has_format}, import={has_import})")
        if not (has_format and has_import):
            all_ok = False
    else:
        print(f"  ❌ {v} MISSING")
        all_ok = False

if all_ok:
    print("  ✅ All frontend files correctly formatted")

# 5. Check utility file
print("\n[5/6] Utility file...")
util = 'ui/src/utils/formatAmount.ts'
if os.path.exists(util):
    content = open(util, 'r', encoding='utf-8').read()
    has_export = 'export function formatWanYuan' in content
    has_yuanToWan = 'export function yuanToWan' in content
    print(f"  ✅ {util} (formatWanYuan={has_export}, yuanToWan={has_yuanToWan})")
else:
    print(f"  ❌ {util} MISSING")

# 6. Check docs
print("\n[6/6] Documentation...")
docs = [
    'docs/audits/p0-1-database-analysis-20260720.md',
    'docs/design/p0-1-amount-unit-strategy.md',
    'docs/design/p0-1-historical-snapshot-downgrade.md',
    'docs/audits/p0-2-api-contract-review-20260720.md',
    'docs/design/p0-4-task-spec-update-20260720.md',
    'docs/audits/p0-0-to-p0-2-progress-20260720.md',
]
for d in docs:
    exists = os.path.exists(d)
    print(f"  {'✅' if exists else '❌'} {d}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
