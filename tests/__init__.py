"""Unit tests for the repo-deep-dive pack (stdlib ``unittest``).

Run with::

    python3 -m unittest discover -s tests -v

The suite exercises the parsing, inventory, and deterministic-check logic that
the smoke harness (``tools/self_test.sh``) only covers indirectly. It uses only
the standard library plus ``git`` for the portability check, so it runs anywhere
the pack's shell harness runs (TEST-P3-004).
"""
