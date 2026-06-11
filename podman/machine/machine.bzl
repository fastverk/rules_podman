"""`podman_machine` — a self-managed Podman service VM for macOS.

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
"""

load("@rules_macvm//image:defs.bzl", "ignition_config")
load("@rules_macvm//vm:defs.bzl", "vm")

def podman_machine(
        name,
        image,
        ssh_authorized_keys = [],
        enable_units = ["podman.socket"],
        cpus = 2,
        memory = "2GiB",
        rosetta = True,
        socket = "$VM_RUNTIME/podman.sock",
        extra_devices = [],
        provider = None,
        visibility = None,
        **kwargs):
    """Declare a self-managed Podman service VM.

    Args:
      name: target name; `bazel run //:<name>` boots the VM.
      image: a bootable Podman/FCOS disk image (EFI-booted as virtio-blk).
      ssh_authorized_keys: SSH public keys to authorize in the guest.
      enable_units: systemd units to enable (default: `podman.socket`).
      cpus: virtual CPUs.
      memory: guest RAM, e.g. "2GiB".
      rosetta: expose Rosetta x86-64 translation (Apple Silicon).
      socket: host path for the forwarded Podman API socket. Default is a
        per-boot ephemeral path; pass a stable path for a durable
        CONTAINER_HOST across boots.
      extra_devices: extra raw vfkit `--device` specs.
      provider: VMM backend override (defaults to the registered
        rules_macvm toolchain, i.e. @vfkit on macOS). Tests pass the mock.
      visibility: target visibility.
      **kwargs: forwarded to the underlying `vm` rule.
    """
    ignition_config(
        name = name + ".ignition",
        ssh_authorized_keys = ssh_authorized_keys,
        enable_units = enable_units,
    )

    devices = [
        "virtio-net,nat",
        "virtio-vsock,port=1024,socketURL=unix://" + socket,
    ] + extra_devices

    vm(
        name = name,
        cpus = cpus,
        devices = devices,
        disks = [image],
        efi = True,
        ignition = name + ".ignition",
        memory = memory,
        provider = provider,
        rosetta = rosetta,
        visibility = visibility,
        **kwargs
    )
