#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261120 entry.

Copies the held front-page image (entry.png, rendered by render_image.py)
into the output directory, byte for byte. Standard library only, no
network access, no work done at run time beyond the copy — so repeated
runs always produce identical output.

The output directory defaults to /output and can be overridden with the
MAKEFUN_OUTPUT_DIR environment variable.
"""

import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        print(f"error: {source} is missing", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
