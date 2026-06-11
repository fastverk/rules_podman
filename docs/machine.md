<!-- Generated with Stardoc: http://skydoc.bazel.build -->

`podman_machine` — a self-managed Podman service VM for macOS.

On Linux, rules_podman is daemonless (the static engine forks the OCI
runtime directly). macOS has no Linux kernel, so the podman *service*
must run inside a Linux VM. This macro composes `rules_macvm` to provide
that VM hermetically and reproducibly — the Docker-Desktop / `podman
machine` architecture, but pinned and Bazel-native:

1. `ignition_config` renders provisioning (inject an SSH key, enable
   `podman.socket`) entirely from attrs.
2. `vm` EFI-boots a bootable Podman/Fedora-CoreOS `image` with that
   Ignition, exposing the Podman API socket over virtio-vsock and NAT
   networking.

`bazel run //:<name>` boots it; point the client at the socket
(`CONTAINER_HOST=unix://<socket>`) and rules_podman's `podman_run` /
`podman_build` / `podman_image_load` drive containers inside it.

VALIDATION BOUNDARY: the rendered Ignition and the VM spec/argv are
golden-tested. The live boot + connect path needs a real Mac and a
bootable Podman image, and is NOT exercised in CI (Apple
Virtualization.framework can't run in cloud CI). Treat the boot path as
unvalidated until run on hardware.

<a id="podman_machine"></a>

## podman_machine

<pre>
load("@rules_podman//podman/machine:machine.bzl", "podman_machine")

podman_machine(<a href="#podman_machine-name">name</a>, <a href="#podman_machine-image">image</a>, <a href="#podman_machine-ssh_authorized_keys">ssh_authorized_keys</a>, <a href="#podman_machine-enable_units">enable_units</a>, <a href="#podman_machine-cpus">cpus</a>, <a href="#podman_machine-memory">memory</a>, <a href="#podman_machine-rosetta">rosetta</a>, <a href="#podman_machine-socket">socket</a>,
               <a href="#podman_machine-extra_devices">extra_devices</a>, <a href="#podman_machine-provider">provider</a>, <a href="#podman_machine-visibility">visibility</a>, <a href="#podman_machine-kwargs">**kwargs</a>)
</pre>

Declare a self-managed Podman service VM.

**PARAMETERS**


| Name  | Description | Default Value |
| :------------- | :------------- | :------------- |
| <a id="podman_machine-name"></a>name |  target name; `bazel run //:<name>` boots the VM.   |  none |
| <a id="podman_machine-image"></a>image |  a bootable Podman/FCOS disk image (EFI-booted as virtio-blk).   |  none |
| <a id="podman_machine-ssh_authorized_keys"></a>ssh_authorized_keys |  SSH public keys to authorize in the guest.   |  `[]` |
| <a id="podman_machine-enable_units"></a>enable_units |  systemd units to enable (default: `podman.socket`).   |  `["podman.socket"]` |
| <a id="podman_machine-cpus"></a>cpus |  virtual CPUs.   |  `2` |
| <a id="podman_machine-memory"></a>memory |  guest RAM, e.g. "2GiB".   |  `"2GiB"` |
| <a id="podman_machine-rosetta"></a>rosetta |  expose Rosetta x86-64 translation (Apple Silicon).   |  `True` |
| <a id="podman_machine-socket"></a>socket |  host path for the forwarded Podman API socket. Default is a per-boot ephemeral path; pass a stable path for a durable CONTAINER_HOST across boots.   |  `"$VM_RUNTIME/podman.sock"` |
| <a id="podman_machine-extra_devices"></a>extra_devices |  extra raw vfkit `--device` specs.   |  `[]` |
| <a id="podman_machine-provider"></a>provider |  VMM backend override (defaults to the registered rules_macvm toolchain, i.e. @vfkit on macOS). Tests pass the mock.   |  `None` |
| <a id="podman_machine-visibility"></a>visibility |  target visibility.   |  `None` |
| <a id="podman_machine-kwargs"></a>kwargs |  forwarded to the underlying `vm` rule.   |  none |


