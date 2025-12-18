#⭐#
from __future__ import annotations

import sys
import pathlib
import argparse
from typing import Iterable


def is_python_file(path: pathlib.Path) -> bool:
    return path.suffix == ".py" and path.is_file()


def iter_import_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """
    Return (start, end) line indices (0-based, end exclusive) for contiguous
    import blocks consisting only of lines that start with 'import ' or 'from '.
    """
    blocks: list[tuple[int, int]] = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].startswith("import ") or lines[i].startswith("from "):
            start = i
            i += 1
            while i < n and (lines[i].startswith("import ") or lines[i].startswith("from ")):
                i += 1
            blocks.append((start, i))
        else:
            i += 1
    return blocks


def add_blank_lines_every_n(import_lines: list[str], n: int = 5) -> list[str]:
    """
    Insert a single blank line after every n-th import line.
    Ensures no trailing blank line at the end of the block.
    """
    result: list[str] = []
    for idx, line in enumerate(import_lines, start=1):
        result.append(line)
        if idx % n == 0:
            result.append("\n")

    while result and result[-1] == "\n":
        result.pop()

    return result


def normalize_block(block_lines: list[str], n: int = 5) -> list[str]:
    """
    Canonical form of an import block:
    - remove all blank lines
    - ensure __future__ imports stay first
    - sort by line length (Windows-safe)
    - insert a blank line after every n imports
    """
    imports_only = [ln for ln in block_lines if ln.strip() != ""]

    def sort_key(line: str) -> tuple[int, int]:
        clean = line.rstrip()
        is_future = 0 if clean.startswith("from __future__ import") else 1
        return (is_future, len(clean))

    indexed = list(enumerate(imports_only))
    indexed_sorted = sorted(
        indexed,
        key=lambda t: (sort_key(t[1]), t[0]),  # stable + deterministic
    )

    imports_sorted = [line for _, line in indexed_sorted]
    return add_blank_lines_every_n(imports_sorted, n=n)



MARKER = "#⭐#"


def ensure_star_at_top(lines: list[str]) -> bool:
    # Handle BOM if present anyway
    first = lines[0].lstrip("\ufeff") if lines else ""
    if lines and first.strip() == MARKER:
        return False

    lines.insert(0, f"{MARKER}\n")
    return True


def check_file(path: pathlib.Path, fix: bool, group_size: int = 5) -> bool:
    # utf-8-sig strips BOM on Windows so MARKER detection works reliably
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines(keepends=True)

    changed = False
    offset = 0

    # Normalize each contiguous import block
    for start, end in iter_import_blocks(lines):
        start += offset
        end += offset

        current_block = lines[start:end]
        desired_block = normalize_block(current_block, n=group_size)

        if current_block != desired_block:
            if not fix:
                print(f"{path}: import block not normalized (lines {start+1}-{end})")
                return False

            lines[start:end] = desired_block
            offset += len(desired_block) - (end - start)
            changed = True

    # Prepend marker at the very top (literal line 1)
    if ensure_star_at_top(lines):
        changed = True

    if changed:
        path.write_text("".join(lines), encoding="utf-8")
        print(f"{path}: applied suggested edits; stage them to accept")
        return False  # fail commit so user must explicitly stage

    return True  # no changes needed


def main(argv: Iterable[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fix", action="store_true", help="Rewrite files to enforce ordering")
    p.add_argument("--group-size", type=int, default=5, help="Blank line after every N imports")
    p.add_argument("files", nargs="*")
    args = p.parse_args(list(argv))

    ok = True
    for f in args.files:
        path = pathlib.Path(f)
        if is_python_file(path):
            ok = check_file(path, fix=args.fix, group_size=args.group_size) and ok

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
