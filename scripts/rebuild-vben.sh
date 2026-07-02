#!/bin/bash
# rebuild-vben.sh: Rebuild Vben frontend web-antd
# Usage: bash scripts/rebuild-vben.sh

set -e
export PATH="$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"
PNPM=$(command -v pnpm)
echo "pnpm: $PNPM ($($PNPM --version))"

cd /home/samuel/.openclaw/workspace/pm-director/ui-vben

echo "=== Building @vben/web-antd ==="
$PNPM -F @vben/web-antd build

echo "=== Verification ==="
ls -la apps/web-antd/dist/index.html
ls -la apps/web-antd/dist/js/contracts-*.js
ls -la apps/web-antd/dist/js/invoices-*.js
ls -la apps/web-antd/dist/js/suppliers-*.js
echo "=== Build Complete ==="
