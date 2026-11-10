# -*- coding: utf-8 -*-
"""Veilige I/O voor onderzoek-scripts: UTF-8, lock-check, atomair schrijven."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def force_utf8_stdio() -> None:
    """Voorkom charmap/UnicodeEncodeError in Windows-terminals."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def is_locked(path: Path) -> bool:
    """True als een bestaand bestand niet exclusief te openen is (vaak open in viewer)."""
    path = Path(path)
    if not path.exists():
        return False
    try:
        with open(path, "a+b"):
            pass
        return False
    except OSError:
        return True


def wait_unlocked(path: Path, timeout_s: float = 8.0, poll_s: float = 0.25) -> bool:
    """Wacht tot pad vrij is. True = vrij, False = nog vergrendeld."""
    path = Path(path)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if not is_locked(path):
            return True
        time.sleep(poll_s)
    return not is_locked(path)


def write_bytes_atomic(path: Path, data: bytes, retries: int = 5) -> Path:
    """Schrijf via .tmp + replace; controleer eerst of doel niet vergrendeld is."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not wait_unlocked(path, timeout_s=6.0):
        raise PermissionError(
            f"Bestand vergrendeld (open in browser/editor?): {path}"
        )
    tmp = path.with_suffix(path.suffix + ".tmp")
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            if tmp.exists() and not wait_unlocked(tmp, timeout_s=2.0):
                tmp = path.with_suffix(f"{path.suffix}.tmp{attempt}")
            tmp.write_bytes(data)
            os.replace(tmp, path)
            return path
        except OSError as err:
            last_err = err
            time.sleep(0.35 * (attempt + 1))
    raise PermissionError(f"Kon niet schrijven naar {path}: {last_err}")


def write_text_utf8(path: Path, text: str, retries: int = 5) -> Path:
    """Schrijf tekst altijd als UTF-8 (met BOM-vrij)."""
    return write_bytes_atomic(path, text.encode("utf-8"), retries=retries)


def wait_file_ready(path: Path, min_bytes: int = 1000, timeout_s: float = 20.0) -> Path:
    """Wacht tot een bestand bestaat, niet meer groeit, en groot genoeg is (Chrome-race)."""
    path = Path(path)
    deadline = time.time() + timeout_s
    last_size = -1
    stable = 0
    while time.time() < deadline:
        if path.exists():
            try:
                size = path.stat().st_size
            except OSError:
                size = -1
            if size >= min_bytes:
                if size == last_size:
                    stable += 1
                    if stable >= 2:
                        return path
                else:
                    stable = 0
                    last_size = size
        time.sleep(0.3)
    raise FileNotFoundError(
        f"Bestand niet klaar binnen {timeout_s:.0f}s: {path} "
        f"(exists={path.exists()})"
    )
