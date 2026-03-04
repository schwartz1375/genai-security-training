"""Local model setup utilities consistent with prior labs."""

from __future__ import annotations

try:
    import torch
except Exception:  # Optional at import time for notebook UX.
    torch = None


def select_device() -> str:
    if torch is None:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def langgraph_available() -> bool:
    import sys

    # LangChain/LangGraph transitive dependencies may warn on Python 3.14+.
    # For training UX, prefer fallback orchestration on these runtimes.
    if sys.version_info >= (3, 14):
        return False
    try:
        import langgraph  # noqa: F401

        return True
    except Exception:
        return False
