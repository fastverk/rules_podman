# Changelog

All notable changes to rules_podman. The format is loosely
[Keep a Changelog](https://keepachangelog.com/) — version headers
mirror the published bazel-registry entries.

## 0.0.1

- Initial scaffold via `rels scaffold`.
- Module extension `@rules_podman//podman:extensions.bzl%podman` that
  hermetically fetches Podman (5.8.2, pinned by sha256) for
  Linux/macOS/Windows on amd64 + arm64, and emits `@podman//:podman`
  plus a registerable `@podman//:podman_toolchain_def`.
  - **Linux: daemonless.** Fetches the fully-static, rootless
    `mgoltzsche/podman-static` bundle (podman + crun/runc + conmon +
    netavark + pasta + fuse-overlayfs) and generates a launcher wiring
    podman to the bundled runtimes/helpers/configs. No service required.
  - macOS/Windows: the official `containers/podman` client (drives a
    `podman machine`; daemonless isn't possible without a Linux kernel).
- Toolchain `@rules_podman//podman:toolchain_type` + `podman_toolchain`
  rule (carries an `engine` flag), swappable via `register_toolchains(...)`.
- Rules `podman_run`, `podman_build`, `podman_image_load` in
  `//podman:defs.bzl`, each resolving the binary through the toolchain
  and accepting `url`/`connection`/`extra_args`. `podman_run`/`_build`/
  `_image_load` also take `storage = default|ephemeral|workspace` to
  isolate the container store (`--root`/`--runroot`/`--storage-driver=vfs`)
  on engine toolchains.
- `tools/refresh_versions.py` re-pins a version across both upstreams
  via the GitHub releases API; stardoc-generated reference under `docs/`;
  `//examples/smoke` coverage (`podman --version` test + build_test, plus
  a `:daemonless` run-only demo).
