#!/usr/bin/env python3
"""
Compile a multi-view Capsule from a source model.

This is the stable CLI entry point for the current presentation compiler. The
renderer implementation still lives in compile_multiview_demo.py while the
presentation model is being studied.

Usage:
  compile_multiview.py examples/multiview_chat_summary.json -o capsule.html
"""

from compile_multiview_demo import main


if __name__ == "__main__":
    main()
