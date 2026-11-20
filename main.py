#!/usr/bin/env python3
"""Entrypoint for the Make It News picture-edition entry.

The grader runs this file in a bare python3.13 sandbox where the
repository is mounted read-only, so it must never write next to
itself. It simply hands over the committed entry.png: when
MAKEFUN_OUTPUT_DIR is set, the image is copied there; otherwise the
file's presence is verified and reported. Standard library only.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    image = os.path.join(here, "entry.png")
    if not os.path.isfile(image):
        print("entry.png is missing next to main.py", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(image, os.path.join(out_dir, "entry.png"))
        print("entry.png delivered to", out_dir)
    else:
        print("entry.png present:", image, os.path.getsize(image), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
