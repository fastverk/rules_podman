#!/usr/bin/env bash
# Fake VMM for the podman_machine example. Prints its argv and exits 0,
# so the machine's provisioning + VM spec are tested hermetically (no
# Apple Virtualization.framework). rules_macvm ships its own mock too,
# but that one is dev-only there and invisible to consumers — so we bring
# our own.
set -euo pipefail

echo "mock-vmm: boot"
for a in "$@"; do
  echo "arg: $a"
done
echo "mock-vmm: ok"
