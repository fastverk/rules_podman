<!-- Generated with Stardoc: http://skydoc.bazel.build -->

Toolchain rule for rules_podman.

`podman_toolchain` wraps a hermetically-fetched Podman binary as a
single Bazel toolchain. The user-facing rules (`podman_run`,
`podman_build`, `podman_image_load`) resolve their client through
`@rules_podman//podman:toolchain_type`, so a custom Podman (a
locally-built engine, a distro package, a different pinned version) can
be swapped in via `register_toolchains(...)` without touching rule
attributes.

The `engine` field tells the rules whether this is a real local engine
(Linux daemonless bundle) or a remote client (macOS/Windows). Storage
isolation (`--root`/`--runroot`/`--storage-driver`) is only injected for
engine toolchains — those flags are server-side and ignored by a client.

The module extension at `@rules_podman//podman:extensions.bzl`
generates a default toolchain (`@podman//:podman_toolchain_def`).
Register it from `MODULE.bazel`:

    register_toolchains("@podman//:podman_toolchain_def")

<a id="podman_toolchain"></a>

## podman_toolchain

<pre>
load("@rules_podman//podman:toolchains.bzl", "podman_toolchain")

podman_toolchain(<a href="#podman_toolchain-name">name</a>, <a href="#podman_toolchain-engine">engine</a>, <a href="#podman_toolchain-podman">podman</a>, <a href="#podman_toolchain-version">version</a>)
</pre>

Declare a Podman binary as a Bazel toolchain.

**ATTRIBUTES**


| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="podman_toolchain-name"></a>name |  A unique name for this target.   | <a href="https://bazel.build/concepts/labels#target-names">Name</a> | required |  |
| <a id="podman_toolchain-engine"></a>engine |  True if this binary is a local daemonless engine; False for a remote client. Gates storage-isolation flag injection in the rules.   | Boolean | optional |  `False`  |
| <a id="podman_toolchain-podman"></a>podman |  The podman executable target.   | <a href="https://bazel.build/concepts/labels">Label</a> | required |  |
| <a id="podman_toolchain-version"></a>version |  The Podman release version of this binary. Informational; surfaced on PodmanToolchainInfo for diagnostics.   | String | optional |  `""`  |


<a id="PodmanToolchainInfo"></a>

## PodmanToolchainInfo

<pre>
load("@rules_podman//podman:toolchains.bzl", "PodmanToolchainInfo")

PodmanToolchainInfo(<a href="#PodmanToolchainInfo-podman">podman</a>, <a href="#PodmanToolchainInfo-version">version</a>, <a href="#PodmanToolchainInfo-engine">engine</a>)
</pre>

A Podman binary, resolved via a toolchain.

**FIELDS**

| Name  | Description |
| :------------- | :------------- |
| <a id="PodmanToolchainInfo-podman"></a>podman |  Target: the podman executable (a daemonless launcher on Linux, the client binary on macOS/Windows).    |
| <a id="PodmanToolchainInfo-version"></a>version |  String: the Podman release version this binary reports (e.g. "5.8.2"). Empty for custom toolchains that don't set it.    |
| <a id="PodmanToolchainInfo-engine"></a>engine |  Bool: True if this is a local daemonless engine (forks the OCI runtime directly); False for a remote client that needs a `podman machine` / reachable service.    |


