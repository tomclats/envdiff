"""Parse env files and report key differences. Values stay in memory."""

from __future__ import annotations

import re
from pathlib import Path

KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class EnvError(Exception):
    """A file is not a usable env file."""


def load_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise EnvError(f"{path} not found")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise EnvError(f"{path}: {exc.strerror}") from exc
    values: dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line == "" or line.startswith("#"):
            continue
        if line.startswith("export ") or line.startswith("export\t"):
            line = line.split(None, 1)[1].strip()
        if "=" not in line:
            raise EnvError(f"{path}: line {number}: not a KEY=VALUE line")
        key, value = line.split("=", 1)
        key = key.strip()
        if KEY.fullmatch(key) is None:
            raise EnvError(f"{path}: line {number}: invalid key {key}")
        if key in values:
            raise EnvError(f"{path}: line {number}: duplicate key {key}")
        values[key] = unquote(value.strip())
    return values


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def labels(left: str, right: str) -> tuple[str, str]:
    left_name = Path(left).name
    right_name = Path(right).name
    if left_name == right_name:
        return left, right
    return left_name, right_name


def render_diff(left_label: str, left: dict[str, str], right_label: str, right: dict[str, str]) -> str:
    only_left = sorted(set(left) - set(right))
    only_right = sorted(set(right) - set(left))
    both = set(left) & set(right)
    differ = sorted(key for key in both if left[key] != right[key])
    same = sum(1 for key in both if left[key] == right[key])
    lines = [f"ONLY {left_label}  {key}" for key in only_left]
    lines.extend(f"ONLY {right_label}  {key}" for key in only_right)
    lines.extend(f"DIFFER  {key}" for key in differ)
    lines.append(f"SAME  {same}")
    return "\n".join(lines) + "\n"
