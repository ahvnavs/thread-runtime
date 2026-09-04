"""Capability detection model using standard library introspection."""

from __future__ import annotations

import os
import platform
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SystemCapabilities:
    """Platform and runtime capabilities model."""

    os_name: str
    os_release: str
    cpu_architecture: str
    cpu_cores: int | None
    memory_status: str
    python_version: str
    interactive_stdin: bool
    interactive_stdout: bool
    color_supported: bool
    unicode_supported: bool
    cwd_writable: bool


def detect_capabilities() -> SystemCapabilities:
    """Detect current system environment capabilities cleanly."""
    os_name = platform.system() or "Unknown"
    os_release = platform.release() or "Unknown"
    cpu_arch = platform.machine() or platform.processor() or "Unknown"

    try:
        cpu_cores = os.cpu_count()
    except Exception:
        cpu_cores = None

    # Memory detection fallback using Linux /proc/meminfo if available
    memory_status = "UNKNOWN"
    if os_name == "Linux" and Path("/proc/meminfo").is_file():
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        parts = line.split()
                        kb = int(parts[1])
                        gb = kb / (1024 * 1024)
                        memory_status = f"{gb:.1f} GB Total"
                        break
        except Exception:
            memory_status = "UNKNOWN"

    python_ver = sys.version.split()[0]

    interactive_in = hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
    interactive_out = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    # Color support detection
    color_supported = False
    if interactive_out:
        term = os.environ.get("TERM", "").lower()
        colorterm = os.environ.get("COLORTERM", "").lower()
        no_color = os.environ.get("NO_COLOR")
        if not no_color and (colorterm in ("truecolor", "24bit") or term not in ("dumb", "")):
            color_supported = True

    # Unicode support check
    unicode_supported = False
    encoding = getattr(sys.stdout, "encoding", None)
    if encoding and "utf" in encoding.lower():
        unicode_supported = True

    # Working directory writable check
    cwd_writable = False
    try:
        with tempfile.TemporaryFile(dir=Path.cwd()):
            cwd_writable = True
    except Exception:
        cwd_writable = False

    return SystemCapabilities(
        os_name=os_name,
        os_release=os_release,
        cpu_architecture=cpu_arch,
        cpu_cores=cpu_cores,
        memory_status=memory_status,
        python_version=python_ver,
        interactive_stdin=interactive_in,
        interactive_stdout=interactive_out,
        color_supported=color_supported,
        unicode_supported=unicode_supported,
        cwd_writable=cwd_writable,
    )
