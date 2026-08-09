"""Pytest configuration for the Mayasari Bakery Analysis project.

Ensures the repository root is available on sys.path so tests can
import project modules through the `src` namespace.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
