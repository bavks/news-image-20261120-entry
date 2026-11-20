#!/usr/bin/env python3
"""Entry point for the *Make It News* make.fun submission.

Running this file rebuilds the newspaper front page from scratch --
every headline, column and illustration is typeset and drawn by
`render_image.py` at run time -- and writes the result to `entry.png`
next to this file.  It then reports the finished image's dimensions
and file size so a bad render is obvious from the console alone.

Usage:  python3 main.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import render_image


def produce_front_page():
    """Render the page and save it as entry.png beside this script."""
    target = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "entry.png")
    picture = render_image.build_page()
    picture.save(target, format="PNG", optimize=True)
    return target, picture.size, os.path.getsize(target)


if __name__ == "__main__":
    path, (w, h), nbytes = produce_front_page()
    print(f"Make It News front page -> {path} ({w}x{h}, {nbytes} bytes)")
