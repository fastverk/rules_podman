#!/usr/bin/env bash
# Regenerate docs/{defs,extensions,toolchains}.md from stardoc output.
# Run after changing rule docstrings. Invoked via `bazel run //docs:update`.
set -euo pipefail

if [[ -z "${BUILD_WORKSPACE_DIRECTORY:-}" ]]; then
  echo "error: must be invoked via 'bazel run //docs:update'" >&2
  exit 1
fi

RUNFILES_DIR="${RUNFILES_DIR:-$0.runfiles}"

for name in defs extensions toolchains machine; do
  gen="$(find "$RUNFILES_DIR" -name "${name}.md.generated" -print -quit)"
  cp "$gen" "$BUILD_WORKSPACE_DIRECTORY/docs/${name}.md"
done

echo "docs/{defs,extensions,toolchains,machine}.md regenerated."
