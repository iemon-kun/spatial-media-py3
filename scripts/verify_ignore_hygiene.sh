#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "HYGIENE: FAIL - $1" >&2
  exit 1
}

pass() {
  echo "HYGIENE: PASS - $1"
}

# 1) Common local artifacts must not be tracked.
tracked_noise="$(git ls-files | rg '(^|/)\.DS_Store$|(^|/)__pycache__/|\.py[co]$' || true)"
if [[ -n "${tracked_noise}" ]]; then
  echo "${tracked_noise}" >&2
  fail "tracked noise files detected"
fi
pass "no tracked noise files"

# 2) Ignore rules should cover expected local artifacts.
check_ignored_paths=(
  ".DS_Store"
  ".venv"
  "build"
  "dist"
  "__pycache__"
  "memo.txt"
)

for p in "${check_ignored_paths[@]}"; do
  if ! git check-ignore -q "$p"; then
    fail "path is not ignored as expected: $p"
  fi
done
pass "expected paths are ignored"

# 3) Build config and icon are source assets for app packaging and should be tracked.
for p in "Spatial Media Metadata Injector.spec" "app.icns"; do
  if ! git ls-files --error-unmatch "$p" >/dev/null 2>&1; then
    fail "required tracked build asset missing: $p"
  fi
done
pass "build assets are tracked"

echo "HYGIENE: PASS"
