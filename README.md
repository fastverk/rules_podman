# rules_podman

Hermetic, Bazel-idiomatic Podman: a pinned, **daemonless** Podman
toolchain plus `bazel run` rules for running, building, and loading
container images.

## Status: v0.0.1

- A module extension that hermetically fetches Podman for the host
  platform, sha256-pinned (Linux amd64/arm64, macOS amd64/arm64,
  Windows amd64/arm64).
- A Bazel toolchain (`@rules_podman//podman:toolchain_type`) so the
  binary is swappable via `register_toolchains(...)`.
- Three rules: `podman_run`, `podman_build`, `podman_image_load`, with
  opt-in isolated container stores.

See [CHANGELOG.md](CHANGELOG.md) for what has shipped and
[docs/](docs/) for generated rule reference.

## Daemonless on Linux

On **Linux** the toolchain is the fully-static, rootless
[`mgoltzsche/podman-static`](https://github.com/mgoltzsche/podman-static)
bundle — podman plus its own OCI runtime (crun/runc), conmon, netavark,
pasta, aardvark-dns, and fuse-overlayfs. There is **no daemon and no
service**: `podman` forks conmon → crun directly. rules_podman fetches
and pins the whole bundle and generates a launcher that points podman at
the bundled runtimes, helpers, and configs. This is a genuine,
self-contained, hermetic container engine.

On **macOS / Windows** the toolchain is the official `containers/podman`
client. Those OSes have no Linux kernel, so Podman can only run Linux
containers through a `podman machine` VM (which runs a service inside) —
**daemonless is not possible there**, by the nature of the platform. The
client is still fetched + pinned hermetically and is handy for local
development; point it at a machine via `CONTAINER_HOST`, the rules'
`url` / `connection` attributes, or `podman machine start`.

So: on Linux (CI, prod) you get a hermetic daemonless engine; on a Mac
or Windows dev box you get a pinned client that drives a local machine.

### Self-managed machine on macOS (`podman_machine`)

Instead of "bring your own `podman machine`", `//podman/machine:machine.bzl`
provides a **self-managed, pinned** Podman service VM on macOS by
composing [rules_macvm](https://github.com/fastverk/rules_macvm): it
renders an Ignition file (inject an SSH key, enable `podman.socket`) and
EFI-boots a bootable Podman/FCOS image via vfkit, exposing the API socket
over vsock. Point `CONTAINER_HOST` at that socket and the rules below
drive containers inside it.

```python
load("@rules_podman//podman/machine:machine.bzl", "podman_machine")

podman_machine(
    name = "machine",
    image = "//path:fcos.raw",              # a bootable Podman/FCOS disk
    ssh_authorized_keys = ["ssh-ed25519 AAAA… you@host"],
)
```

The rendered Ignition and the VM spec are golden-tested, but the **live
boot/connect path is not exercised in CI** (Apple Virtualization.framework
can't run there) — validate on a Mac with a real bootable image. Windows
still uses bring-your-own WSL2 machine.

### Hermetic container stores

The rules take a `storage` attribute (engine toolchains only):

- `default` — podman's standard rootless store (shared, persists).
- `ephemeral` — a throwaway `vfs` store per invocation (`--root`/
  `--runroot`/`--storage-driver=vfs`), removed on exit. Host-independent
  and reproducible.
- `workspace` — a persistent store under `$BUILD_WORKSPACE_DIRECTORY`.

(`vfs` is used for isolation because it needs no `/dev/fuse` or extra
privileges — it runs anywhere, including locked-down CI.)

## Install

`.bazelrc`:

```
common --registry=https://raw.githubusercontent.com/fastverk/bazel-registry/main/
common --registry=https://bcr.bazel.build/
```

`MODULE.bazel`:

```python
bazel_dep(name = "rules_podman", version = "0.0.1")

podman = use_extension("@rules_podman//podman:extensions.bzl", "podman")
# Optional: pin a specific Podman version (defaults to the bundled pin).
# podman.toolchain(version = "5.8.2")
use_repo(podman, "podman")
register_toolchains("@podman//:podman_toolchain_def")
```

## Usage

```python
load("@rules_podman//podman:defs.bzl", "podman_run", "podman_build", "podman_image_load")

# `bazel run //:podman -- ps -a` — args forwarded verbatim. Daemonless on Linux.
podman_run(name = "podman")

# `bazel run //:image` — stage the context + `podman build`, in a clean store.
podman_build(
    name = "image",
    srcs = ["Containerfile", "app/server.py"],
    image_tags = ["registry.example.com/app:latest"],
    storage = "ephemeral",
    # build_args = {"VERSION": "1.2.3"},
)

# `bazel run //:load` — `podman load -i` an OCI/docker archive
# (e.g. the output of @rules_oci's oci_load).
podman_image_load(
    name = "load",
    image = "//path/to:image.tar",
)
```

Every rule accepts `url` / `connection` to target a specific service and
`extra_args` to bake in flags. The bare binary is available as
`@podman//:podman` if you don't want the launcher ergonomics.

### Linux host notes

The engine is fully self-contained, but rootless Podman still leans on a
few host primitives for *some* workloads: `newuidmap`/`newgidmap` (the
`uidmap` package) for multi-UID containers, and `iptables`/`nsenter` for
certain network modes. Single-UID containers and `pasta` networking work
without them. `podman info` / `build` / `load` need none of it.

## Maintenance

Bump the pinned Podman version (rewrites `podman/private/known_versions.bzl`
across both upstreams):

```
tools/refresh_versions.py            # latest stable
tools/refresh_versions.py --version 5.8.2
```

Regenerate the committed rule docs after editing docstrings:

```
bazel run //docs:update
```
