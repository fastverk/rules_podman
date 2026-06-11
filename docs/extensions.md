<!-- Generated with Stardoc: http://skydoc.bazel.build -->

Module extension for rules_podman.

Hermetically fetches Podman for the host platform, pinned by sha256
(see `private/known_versions.bzl`), and exposes it as `@podman//:podman`
plus a ready-to-register toolchain (`@podman//:podman_toolchain_def`).

On Linux it fetches the fully-static `mgoltzsche/podman-static` bundle
and generates a launcher that wires podman to its **bundled** OCI
runtime (crun), conmon, netavark, and configs — a real **daemonless,
rootless** engine, no service to start. On macOS/Windows it fetches the
official client binary (which talks to a `podman machine`).

Default usage:

    podman = use_extension("@rules_podman//podman:extensions.bzl", "podman")
    use_repo(podman, "podman")
    register_toolchains("@podman//:podman_toolchain_def")

Pin a specific Podman version:

    podman = use_extension("@rules_podman//podman:extensions.bzl", "podman")
    podman.toolchain(version = "5.8.2")
    use_repo(podman, "podman")

<a id="podman"></a>

## podman

<pre>
podman = use_extension("@rules_podman//podman:extensions.bzl", "podman")
podman.toolchain(<a href="#podman.toolchain-version">version</a>)
</pre>

Sets up @podman: a daemonless static engine on Linux, the official client on macOS/Windows.


**TAG CLASSES**

<a id="podman.toolchain"></a>

### toolchain

**Attributes**

| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="podman.toolchain-version"></a>version |  Override the Podman version. Defaults to the value in known_versions.bzl.   | String | optional |  `""`  |


