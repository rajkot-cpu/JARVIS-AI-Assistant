# apps/windows-cc/metrics.py
from __future__ import annotations

import psutil


def snapshot() -> dict:
    disk = psutil.disk_usage("/")
    return {
        "cpu_pct": float(psutil.cpu_percent(interval=0.1)),
        "ram_pct": float(psutil.virtual_memory().percent),
        "disk_pct": float(disk.percent),
    }
