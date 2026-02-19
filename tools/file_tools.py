import os
import aiofiles
import re
from typing import Optional, Tuple


_DEFAULT_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))


def _load_allowed_roots() -> list[str]:
    """
    Load allowed filesystem roots from environment.

    - MCP_ALLOWED_ROOTS: comma-separated list of paths.
      Example: "/data,/path/to/project"
    - If not set, defaults to the project root (parent of `tools/`).
    """
    raw = (os.environ.get("MCP_ALLOWED_ROOTS") or "").strip()
    if not raw:
        return [_DEFAULT_ROOT]

    roots: list[str] = []
    for part in raw.split(","):
        p = part.strip()
        if not p:
            continue
        roots.append(os.path.realpath(os.path.expanduser(p)))

    return roots or [_DEFAULT_ROOT]


ALLOWED_ROOTS: list[str] = _load_allowed_roots()


_ROOT_SELECTOR_RE = re.compile(r"^(?P<idx>\d+):(?P<rest>.*)$")

_EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "dist",
    "build",
}


def _commonpath_is_parent(parent: str, child: str) -> bool:
    try:
        return os.path.commonpath([parent, child]) == parent
    except ValueError:
        return False


def _safe_path(user_path: str) -> Optional[Tuple[str, str]]:
    """
    Ensure the path is within one of the allowed roots.

    Supported inputs:
    - Relative paths (resolved against root[0]).
    - Absolute paths (must be inside an allowed root).
    - Indexed paths: "<n>:relative/path" (resolved against root[n]).
    """
    user_path = (user_path or "").strip()

    m = _ROOT_SELECTOR_RE.match(user_path)
    if m:
        idx = int(m.group("idx"))
        rest = (m.group("rest") or "").lstrip("/\\")
        if idx < 0 or idx >= len(ALLOWED_ROOTS):
            return None
        root = ALLOWED_ROOTS[idx]
        target = os.path.realpath(os.path.join(root, rest))
        if _commonpath_is_parent(root, target):
            return target, root
        return None

    # If an absolute path is provided, allow it only if it lives under a permitted root.
    if os.path.isabs(user_path):
        target = os.path.realpath(os.path.expanduser(user_path))
        for root in ALLOWED_ROOTS:
            if _commonpath_is_parent(root, target):
                return target, root
        return None

    # Otherwise, treat as relative to the primary root.
    root = ALLOWED_ROOTS[0]
    target = os.path.realpath(os.path.join(root, user_path))
    if _commonpath_is_parent(root, target):
        return target, root
    return None


async def list_files(subpath: str = "") -> dict:
    """
    Asynchronously list files and folders up to 50 sublevels deep.

    If multiple roots are configured, you can:
    - list a specific root: "<n>:some/subdir"
    - list everything: subpath="" returns a merged list prefixed with "<n>:"
    """
    subpath = (subpath or "").strip()

    def _walk_one(idx: int, root_dir: str, rel: str, max_entries: int = 2000) -> list[str]:
        out: list[str] = []
        target_dir = os.path.realpath(os.path.join(root_dir, rel))
        for current_root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in _EXCLUDED_DIR_NAMES]
            current_rel = os.path.relpath(current_root, root_dir)
            depth = 0 if current_rel == "." else current_rel.count(os.sep) + 1
            for f in files:
                if len(ALLOWED_ROOTS) == 1 and idx == 0:
                    p = os.path.join(current_rel, f)
                    out.append(p)
                else:
                    p = f if current_rel == "." else os.path.join(current_rel, f)
                    out.append(f"{idx}:{p}")
                if len(out) >= max_entries:
                    dirs[:] = []
                    break
            for d in dirs:
                if len(ALLOWED_ROOTS) == 1 and idx == 0:
                    p = os.path.join(current_rel, d) + "/"
                    out.append(p)
                else:
                    p = (d + "/") if current_rel == "." else (os.path.join(current_rel, d) + "/")
                    out.append(f"{idx}:{p}")
                if len(out) >= max_entries:
                    dirs[:] = []
                    break
            if depth >= 50:
                dirs[:] = []
                break
            if len(out) >= max_entries:
                break
        return out

    try:
        # Default: in multi-root mode, return the allowed roots without walking them.
        # Use "<n>:" to list a specific root.
        if subpath == "" and len(ALLOWED_ROOTS) > 1:
            return {
                "status": "success",
                "roots": ALLOWED_ROOTS,
                "files": [],
                "message": "Multiple roots configured. Use '<n>:' (e.g. '0:' or '1:subdir') to list a specific root.",
            }

        safe = _safe_path(subpath)
        if not safe:
            return {"status": "error", "message": "Access denied"}
        target, root_dir = safe

        # Figure out which root we matched (for consistent prefixing when multi-root is configured).
        idx = next((i for i, r in enumerate(ALLOWED_ROOTS) if r == root_dir), 0)
        rel = os.path.relpath(target, root_dir)
        rel = "" if rel == "." else rel
        files = _walk_one(idx, root_dir, rel)

        return {"status": "success", "roots": ALLOWED_ROOTS, "files": sorted(set(files))}
    except Exception as e:
        return {"status": "error", "message": f"Error listing files: {e}"}


async def read_file(filepath: str) -> dict:
    """Asynchronously read and return the contents of a file."""
    safe = _safe_path(filepath)
    if not safe:
        return {"status": "error", "message": "File not found or access denied"}
    target, _root_dir = safe
    if not os.path.isfile(target):
        return {"status": "error", "message": "File not found or access denied"}

    try:
        async with aiofiles.open(target, "r", encoding="utf-8") as f:
            content = await f.read()
            return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": f"Error reading file: {e}"}


async def overwrite_file(filepath: str, content: str) -> dict:
    """Asynchronously overwrite an existing file with new content."""
    safe = _safe_path(filepath)
    if not safe:
        return {"status": "error", "message": "Access denied"}
    target, _root_dir = safe

    try:
        async with aiofiles.open(target, "w", encoding="utf-8") as f:
            await f.write(content)
        return {"status": "success", "message": "File overwritten successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error writing file: {e}"}


async def create_file(filepath: str, content: str) -> dict:
    """Asynchronously create a new file with content, if it doesn't already exist."""
    safe = _safe_path(filepath)
    if not safe:
        return {"status": "error", "message": "Access denied"}
    target, _root_dir = safe

    if os.path.exists(target):
        return {"status": "error", "message": "File already exists"}

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        async with aiofiles.open(target, "w", encoding="utf-8") as f:
            await f.write(content)
        return {"status": "success", "message": "File created successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error creating file: {e}"}
