import json
from pathlib import Path

def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def write_text(path: str, content: str) -> None:
    ensure_dir(str(Path(path).parent))
    Path(path).write_text(content, encoding="utf-8")

def read_text(path: str) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")

def write_json(path: str, data: dict) -> None:
    ensure_dir(str(Path(path).parent))
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")