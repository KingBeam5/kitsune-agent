#!/usr/bin/env bash
# Install the built Kitsune docs site where the dashboard serves it (hermes_cli/docs_dist, not in git).
# Source: the newest successful "Kitsune Docs" run on GitHub (built by .github/workflows/kitsune-docs.yml).
# Needs: gh (authenticated), tar. Usage: scripts/fetch-docs-site.sh [owner/repo]
set -euo pipefail
repo="${1:-KingBeam5/kitsune-agent}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest="$here/hermes_cli/docs_dist"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

run_id="$(gh run list -R "$repo" --workflow kitsune-docs.yml --json databaseId,status,conclusion \
  --jq '[.[] | select(.status=="completed")] | map(select(.conclusion=="success" or .conclusion=="failure")) | .[0].databaseId')"
[ -n "$run_id" ] || { echo "no completed Kitsune Docs run found for $repo" >&2; exit 1; }
echo "downloading site artifact from run $run_id ..."
gh run download "$run_id" -R "$repo" -n github-pages -D "$tmp"
mkdir "$tmp/site"; tar -xf "$tmp/artifact.tar" -C "$tmp/site"
[ -f "$tmp/site/index.html" ] || { echo "artifact has no index.html" >&2; exit 1; }
rm -rf "$dest"; mv "$tmp/site" "$dest"
echo "installed $(find "$dest" -name '*.html' | wc -l) pages into $dest"
