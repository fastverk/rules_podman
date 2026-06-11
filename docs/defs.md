<!-- Generated with Stardoc: http://skydoc.bazel.build -->

User-facing Bazel rules for rules_podman.

Three `bazel run`-friendly wrappers around the Podman binary resolved
through `@rules_podman//podman:toolchain_type`:

- `podman_run`: a thin launcher — exec podman with optional
  `--connection`/`--url`, an optional isolated storage root, and any
  baked-in `extra_args`, forwarding CLI arguments verbatim.
- `podman_build`: stage a tracked build context (the rule's `srcs`)
  into a temp dir and `podman build` it. Inputs are real Bazel deps, so
  edits to the Containerfile / context invalidate the run.
- `podman_image_load`: `podman load -i <tarball>` an OCI/docker archive
  produced elsewhere in the graph (e.g. `@rules_oci`'s `oci_load`).

Daemonless on Linux: the default toolchain there is the static
`mgoltzsche/podman-static` engine, so these rules run containers with no
service — podman forks conmon → crun directly. On macOS/Windows the
toolchain is the official client, which needs a `podman machine`; point
it at one via `CONTAINER_HOST`, `url`/`connection`, or a running machine.

Storage isolation (`storage = "ephemeral"|"workspace"`) injects
`--root`/`--runroot`/`--storage-driver=vfs` so a run gets a clean,
host-independent container store. It only applies to engine toolchains
(those flags are server-side; a remote client ignores them).

For the bare binary depend directly on `@podman//:podman`.

<a id="podman_build"></a>

## podman_build

<pre>
load("@rules_podman//podman:defs.bzl", "podman_build")

podman_build(<a href="#podman_build-name">name</a>, <a href="#podman_build-srcs">srcs</a>, <a href="#podman_build-build_args">build_args</a>, <a href="#podman_build-connection">connection</a>, <a href="#podman_build-containerfile">containerfile</a>, <a href="#podman_build-extra_args">extra_args</a>, <a href="#podman_build-image_tags">image_tags</a>, <a href="#podman_build-storage">storage</a>,
             <a href="#podman_build-storage_dir">storage_dir</a>, <a href="#podman_build-url">url</a>)
</pre>

Build an image from a tracked build context via `bazel run`. Stages `srcs` into a temp context and runs `podman build` (daemonless on Linux).

**ATTRIBUTES**


| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="podman_build-name"></a>name |  A unique name for this target.   | <a href="https://bazel.build/concepts/labels#target-names">Name</a> | required |  |
| <a id="podman_build-srcs"></a>srcs |  The build context: the Containerfile plus everything it COPYs/ADDs. Staged into the build context preserving each file's path relative to this rule's package.   | <a href="https://bazel.build/concepts/labels">List of labels</a> | required |  |
| <a id="podman_build-build_args"></a>build_args |  `--build-arg KEY=VALUE` pairs passed to `podman build`.   | <a href="https://bazel.build/rules/lib/dict">Dictionary: String -> String</a> | optional |  `{}`  |
| <a id="podman_build-connection"></a>connection |  Named Podman system connection to target (`--connection`).   | String | optional |  `""`  |
| <a id="podman_build-containerfile"></a>containerfile |  Path of the Containerfile within the staged context (i.e. relative to this rule's package). Must be among `srcs`.   | String | optional |  `"Containerfile"`  |
| <a id="podman_build-extra_args"></a>extra_args |  Flags appended after the rules_podman defaults but before any args passed on the CLI.   | List of strings | optional |  `[]`  |
| <a id="podman_build-image_tags"></a>image_tags |  Image tags to apply (`-t`). (Named `image_tags`, not `tags`, which is Bazel's reserved target-tags attribute.)   | List of strings | optional |  `[]`  |
| <a id="podman_build-storage"></a>storage |  Container-store isolation (engine/daemonless toolchains only): * `default`: use podman's standard rootless store (shared, persists). * `ephemeral`: a fresh `$TMPDIR/podman_store.XXXXXX` with `--storage-driver=vfs`, removed on exit. Hermetic, but images don't persist across runs. * `workspace`: a persistent store under `$BUILD_WORKSPACE_DIRECTORY/<storage_dir>` (requires `bazel run`).   | String | optional |  `"default"`  |
| <a id="podman_build-storage_dir"></a>storage_dir |  Workspace-relative store path used when `storage = "workspace"`. Defaults to `.cache/rules_podman/<target name>`.   | String | optional |  `""`  |
| <a id="podman_build-url"></a>url |  Podman service URL to target (`--url`), e.g. `unix:///run/podman/podman.sock` or an `ssh://` endpoint. Overrides $CONTAINER_HOST for this invocation.   | String | optional |  `""`  |


<a id="podman_image_load"></a>

## podman_image_load

<pre>
load("@rules_podman//podman:defs.bzl", "podman_image_load")

podman_image_load(<a href="#podman_image_load-name">name</a>, <a href="#podman_image_load-connection">connection</a>, <a href="#podman_image_load-extra_args">extra_args</a>, <a href="#podman_image_load-image">image</a>, <a href="#podman_image_load-storage">storage</a>, <a href="#podman_image_load-storage_dir">storage_dir</a>, <a href="#podman_image_load-url">url</a>)
</pre>

`podman load -i <tarball>` an image archive into the target store via `bazel run`. Use `storage = "workspace"` to load into a persistent store.

**ATTRIBUTES**


| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="podman_image_load-name"></a>name |  A unique name for this target.   | <a href="https://bazel.build/concepts/labels#target-names">Name</a> | required |  |
| <a id="podman_image_load-connection"></a>connection |  Named Podman system connection to target (`--connection`).   | String | optional |  `""`  |
| <a id="podman_image_load-extra_args"></a>extra_args |  Flags appended after the rules_podman defaults but before any args passed on the CLI.   | List of strings | optional |  `[]`  |
| <a id="podman_image_load-image"></a>image |  An OCI-archive or docker-archive tarball to `podman load`, e.g. the output of `@rules_oci`'s `oci_load` rule.   | <a href="https://bazel.build/concepts/labels">Label</a> | required |  |
| <a id="podman_image_load-storage"></a>storage |  Container-store isolation (engine/daemonless toolchains only): * `default`: use podman's standard rootless store (shared, persists). * `ephemeral`: a fresh `$TMPDIR/podman_store.XXXXXX` with `--storage-driver=vfs`, removed on exit. Hermetic, but images don't persist across runs. * `workspace`: a persistent store under `$BUILD_WORKSPACE_DIRECTORY/<storage_dir>` (requires `bazel run`).   | String | optional |  `"default"`  |
| <a id="podman_image_load-storage_dir"></a>storage_dir |  Workspace-relative store path used when `storage = "workspace"`. Defaults to `.cache/rules_podman/<target name>`.   | String | optional |  `""`  |
| <a id="podman_image_load-url"></a>url |  Podman service URL to target (`--url`), e.g. `unix:///run/podman/podman.sock` or an `ssh://` endpoint. Overrides $CONTAINER_HOST for this invocation.   | String | optional |  `""`  |


<a id="podman_run"></a>

## podman_run

<pre>
load("@rules_podman//podman:defs.bzl", "podman_run")

podman_run(<a href="#podman_run-name">name</a>, <a href="#podman_run-connection">connection</a>, <a href="#podman_run-extra_args">extra_args</a>, <a href="#podman_run-storage">storage</a>, <a href="#podman_run-storage_dir">storage_dir</a>, <a href="#podman_run-url">url</a>)
</pre>

Run Podman via `bazel run`. Daemonless on Linux; CLI arguments are forwarded verbatim (`bazel run //:podman -- ps -a`).

**ATTRIBUTES**


| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="podman_run-name"></a>name |  A unique name for this target.   | <a href="https://bazel.build/concepts/labels#target-names">Name</a> | required |  |
| <a id="podman_run-connection"></a>connection |  Named Podman system connection to target (`--connection`).   | String | optional |  `""`  |
| <a id="podman_run-extra_args"></a>extra_args |  Flags appended after the rules_podman defaults but before any args passed on the CLI.   | List of strings | optional |  `[]`  |
| <a id="podman_run-storage"></a>storage |  Container-store isolation (engine/daemonless toolchains only): * `default`: use podman's standard rootless store (shared, persists). * `ephemeral`: a fresh `$TMPDIR/podman_store.XXXXXX` with `--storage-driver=vfs`, removed on exit. Hermetic, but images don't persist across runs. * `workspace`: a persistent store under `$BUILD_WORKSPACE_DIRECTORY/<storage_dir>` (requires `bazel run`).   | String | optional |  `"default"`  |
| <a id="podman_run-storage_dir"></a>storage_dir |  Workspace-relative store path used when `storage = "workspace"`. Defaults to `.cache/rules_podman/<target name>`.   | String | optional |  `""`  |
| <a id="podman_run-url"></a>url |  Podman service URL to target (`--url`), e.g. `unix:///run/podman/podman.sock` or an `ssh://` endpoint. Overrides $CONTAINER_HOST for this invocation.   | String | optional |  `""`  |


