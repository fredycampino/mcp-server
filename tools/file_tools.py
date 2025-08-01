import os
import aiofiles
from typing import Optional


BASE_DIR = os.path.expanduser("~/develop/py/mcp") # Set this to the root directory you allow access to


def _safe_path(subpath: str) -> Optional[str]:
    """Ensure the path is within the allowed base directory."""
    real_base = os.path.realpath(BASE_DIR)
    real_target = os.path.realpath(os.path.join(BASE_DIR, subpath))
    if real_target.startswith(real_base):
        return real_target
    return None


async def list_files(subpath: str = "") -> dict:
    """Asynchronously list files and folders up to 50 sublevels deep under the given subpath."""
    target = _safe_path(subpath)
    if not target:
        return {"status": "error", "message": "Access denied"}

    result = []
    try:
        for root, dirs, files in os.walk(target):
            rel_root = os.path.relpath(root, BASE_DIR)
            for f in files:
                rel_path = os.path.join(rel_root, f)
                result.append(rel_path)
            for d in dirs:
                rel_path = os.path.join(rel_root, d) + "/"
                result.append(rel_path)
            if rel_root.count(os.sep) >= 50:
                break
        return {"status": "success", "files": sorted(result)}
    except Exception as e:
        return {"status": "error", "message": f"Error listing files: {e}"}


async def read_file(filepath: str) -> dict:
    """Asynchronously read and return the contents of a file."""
    target = _safe_path(filepath)
    if not target or not os.path.isfile(target):
        return {"status": "error", "message": "File not found or access denied"}

    try:
        async with aiofiles.open(target, "r", encoding="utf-8") as f:
            content = await f.read()
            return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": f"Error reading file: {e}"}


async def overwrite_file(filepath: str, content: str) -> dict:
    """Asynchronously overwrite an existing file with new content."""
    target = _safe_path(filepath)
    if not target:
        return {"status": "error", "message": "Access denied"}

    try:
        async with aiofiles.open(target, "w", encoding="utf-8") as f:
            await f.write(content)
        return {"status": "success", "message": "File overwritten successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error writing file: {e}"}


async def create_file(filepath: str, content: str) -> dict:
    """Asynchronously create a new file with content, if it doesn't already exist."""
    target = _safe_path(filepath)
    if not target:
        return {"status": "error", "message": "Access denied"}

    if os.path.exists(target):
        return {"status": "error", "message": "File already exists"}

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        async with aiofiles.open(target, "w", encoding="utf-8") as f:
            await f.write(content)
        return {"status": "success", "message": "File created successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error creating file: {e}"}
