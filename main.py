#!/usr/bin/env python3
"""Entry point for the MAKE IT NEWS front page (make.fun news-image-20261120).

The finished front page is committed as ``entry.png`` beside this file.
This program uses only the Python standard library so it can run in a
bare python3.13 sandbox where the repository is mounted read-only:

* it locates ``entry.png`` next to itself and verifies it exists;
* when the ``MAKEFUN_OUTPUT_DIR`` environment variable is set, it
  copies ``entry.png`` into that directory (creating it if needed);
* it never writes into its own directory;
* it prints one confirmation line and exits 0 on success.
"""

import os
import shutil
import sys

IMAGE_NAME = "entry.png"


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, IMAGE_NAME)
    if not os.path.isfile(src):
        print(f"error: {IMAGE_NAME} not found next to main.py",
              file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        dst = os.path.join(out_dir, IMAGE_NAME)
        shutil.copyfile(src, dst)
        print(f"entry.png delivered to {dst} "
              f"({os.path.getsize(dst)} bytes)")
    else:
        print(f"entry.png verified at {src} "
              f"({os.path.getsize(src)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
