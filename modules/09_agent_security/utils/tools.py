"""Realistic local tools for Module 9 labs."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, Dict


def _ensure_demo_workspace(base_dir: str) -> Path:
    root = Path(base_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)

    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "security_notes.txt").write_text(
        "Security baseline: least privilege, explicit tool governance, and audit trails.\n",
        encoding="utf-8",
    )
    return root


def _ensure_demo_db(base_dir: str) -> Path:
    root = _ensure_demo_workspace(base_dir)
    db_path = root / "demo.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)")
    cur.execute("DELETE FROM users")
    cur.executemany(
        "INSERT INTO users (id, username, role) VALUES (?, ?, ?)",
        [(1, "alice", "analyst"), (2, "bob", "engineer"), (3, "charlie", "manager")],
    )
    conn.commit()
    conn.close()
    return db_path


def retrieve_knowledge(query: str, kb: Dict[str, str] | None = None) -> Dict[str, Any]:
    base_kb = {
        "policy": "Use strict allowlists and explicit approvals for risky actions.",
        "incident": "Contain first, then investigate, recover, and add regression tests.",
        "agent": "Never trust inter-agent messages without validation and provenance.",
    }
    if kb:
        base_kb.update(kb)
    return {"ok": True, "data": base_kb.get(query.lower().strip(), "No matching knowledge found.")}


def read_file(path: str, base_dir: str) -> Dict[str, Any]:
    root = _ensure_demo_workspace(base_dir)
    requested = (root / path).resolve()
    if not str(requested).startswith(str(root)):
        return {"ok": False, "error": "Path traversal blocked.", "risk_flags": ["path_traversal"]}
    if not requested.exists() or not requested.is_file():
        return {"ok": False, "error": f"File not found: {path}"}
    return {"ok": True, "data": requested.read_text(encoding="utf-8")}


def query_db(sql: str, base_dir: str) -> Dict[str, Any]:
    db_path = _ensure_demo_db(base_dir)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [c[0] for c in (cur.description or [])]
        return {"ok": True, "data": {"columns": cols, "rows": rows}}
    except Exception as exc:  # sqlite errors are part of attack testing.
        return {"ok": False, "error": f"SQL error: {exc}", "risk_flags": ["sql_error"]}
    finally:
        conn.close()


def append_memory_note(
    note: str,
    memory_path: str,
    conversation_id: str,
    source_agent: str = "executor",
    provenance_tags: list[str] | None = None,
) -> Dict[str, Any]:
    path = Path(memory_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {}
    records = data.setdefault(conversation_id, [])
    records.append(
        {
            "note": note,
            "source_agent": source_agent,
            "provenance_tags": provenance_tags or [],
        }
    )
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"ok": True, "data": f"Memory updated for conversation '{conversation_id}'."}


TOOL_REGISTRY: Dict[str, Callable[..., Dict[str, Any]]] = {
    "retrieve_knowledge": retrieve_knowledge,
    "read_file": read_file,
    "query_db": query_db,
    "append_memory_note": append_memory_note,
}
