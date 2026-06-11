"""Toolchain rule for rules_podman.

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
"""

PodmanToolchainInfo = provider(
    doc = "A Podman binary, resolved via a toolchain.",
    fields = {
        "podman": "Target: the podman executable (a daemonless launcher on " +
                  "Linux, the client binary on macOS/Windows).",
        "version": "String: the Podman release version this binary reports " +
                   "(e.g. \"5.8.2\"). Empty for custom toolchains that don't set it.",
        "engine": "Bool: True if this is a local daemonless engine (forks the " +
                  "OCI runtime directly); False for a remote client that needs a " +
                  "`podman machine` / reachable service.",
    },
)

def _podman_toolchain_impl(ctx):
    return [platform_common.ToolchainInfo(
        podmaninfo = PodmanToolchainInfo(
            podman = ctx.attr.podman,
            version = ctx.attr.version,
            engine = ctx.attr.engine,
        ),
    )]

podman_toolchain = rule(
    implementation = _podman_toolchain_impl,
    attrs = {
        "podman": attr.label(
            executable = True,
            mandatory = True,
            cfg = "exec",
            doc = "The podman executable target.",
        ),
        "version": attr.string(
            default = "",
            doc = "The Podman release version of this binary. Informational; " +
                  "surfaced on PodmanToolchainInfo for diagnostics.",
        ),
        "engine": attr.bool(
            default = False,
            doc = "True if this binary is a local daemonless engine; False for a " +
                  "remote client. Gates storage-isolation flag injection in the rules.",
        ),
    },
    doc = "Declare a Podman binary as a Bazel toolchain.",
)
