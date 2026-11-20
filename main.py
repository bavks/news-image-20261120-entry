#!/usr/bin/env python3
"""Entrypoint for the "Make It News" make.fun entry (news-image-20261120).

The front-page image ships with the repository as ``entry.png`` (it is
produced ahead of time by ``render_image.py``, the authoring tool).  The
grading sandbox runs this file with a bare standard-library-only Python,
no network, and the repository mounted read-only, so this entrypoint does
exactly one thing: hand the finished image to the grader.

Behaviour:
  * Locate ``entry.png`` next to this file.
  * If the ``MAKEFUN_OUTPUT_DIR`` environment variable is set, copy the
    image into that directory (creating it first if necessary), keeping
    the name ``entry.png``.
  * If the variable is not set, simply verify the image is in place.
  * Print one confirmation line and exit 0.  A missing image exits
    non-zero with the reason on stderr.  Nothing is ever written into
    this file's own directory.
"""

import os
import shutil
import sys

IMAGE_NAME = "entry.png"


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, IMAGE_NAME)

    if not os.path.isfile(source):
        print(f"error: {IMAGE_NAME} not found next to main.py ({source})",
              file=sys.stderr)
        return 1

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        target = os.path.join(output_dir, IMAGE_NAME)
        shutil.copyfile(source, target)
        print(f"entrypoint: delivered {IMAGE_NAME} to {target}")
    else:
        print(f"entrypoint: {IMAGE_NAME} present at {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
