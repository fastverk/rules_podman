# rules_podman

Hermetic, Bazel-idiomatic Podman: a pinned podman-client toolchain plus run/build/image-load rules.

## Status: v0.0.1 — scaffold

No public surface yet. See `CHANGELOG.md` for what has shipped.

## Install

`.bazelrc`:

```
common --registry=https://raw.githubusercontent.com/fastverk/bazel-registry/main/
common --registry=https://bcr.bazel.build/
```

`MODULE.bazel`:

```python
bazel_dep(name = "rules_podman", version = "0.0.1")
```
