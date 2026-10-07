"""
Cleanup command module.
Purges developer caches (pip, uv, poetry, npm, pnpm) and empties trash.
"""

import argparse
import platform
import shutil
import subprocess

CLEANUP_TARGETS = [
    {
        "name": "Recycle Bin / Trash",
        "check": lambda: platform.system() == "Windows",
        "cmd": [
            "powershell",
            "-NoProfile",
            "-Command",
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue",
        ],
        "desc": "Windows Recycle Bin",
    },
    {
        "name": "PIP Cache",
        "check": lambda: (
            shutil.which("pip") is not None or shutil.which("python") is not None
        ),
        "cmd": ["pip", "cache", "purge"],
        "desc": "Python PIP package download cache",
    },
    {
        "name": "UV Cache",
        "check": lambda: shutil.which("uv") is not None,
        "cmd": ["uv", "cache", "clean"],
        "desc": "Astral UV wheel and source cache",
    },
    {
        "name": "Poetry Cache",
        "check": lambda: shutil.which("poetry") is not None,
        "cmd": ["poetry", "cache", "clear", "pypi", "--all", "-n"],
        "desc": "Poetry dependency resolution cache",
    },
    {
        "name": "NPM Cache",
        "check": lambda: shutil.which("npm") is not None,
        "cmd": ["npm", "cache", "clean", "--force"],
        "desc": "Node NPM tarball and metadata cache",
    },
    {
        "name": "PNPM Store",
        "check": lambda: shutil.which("pnpm") is not None,
        "cmd": ["pnpm", "store", "prune"],
        "desc": "PNPM unreferenced store packages",
    },
]


def run_cleanup(args: argparse.Namespace) -> int:
    dry_run = getattr(args, "dry_run", False)

    print("=" * 60)
    print(" backpocket: Developer Disk & Cache Cleanup")
    if dry_run:
        print(" [MODE: DRY RUN - no files will be deleted]")
    print("=" * 60)

    total = len(CLEANUP_TARGETS)
    executed = 0
    skipped = 0

    for idx, target in enumerate(CLEANUP_TARGETS, start=1):
        name = target["name"]
        cmd = target["cmd"]
        available = target["check"]()

        print(f"\n[{idx}/{total}] Checking {name}...")

        if not available:
            print("  [-] Tool not found on PATH. Skipped.")
            skipped += 1
            continue

        if dry_run:
            print(f"  [*] Would execute: {' '.join(cmd)}")
            executed += 1
            continue

        print(f"  [*] Executing: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if res.returncode == 0:
                print("  [+] Success.")
            else:
                err_msg = (
                    res.stderr.strip()
                    or res.stdout.strip()
                    or f"exit code {res.returncode}"
                )
                print(f"  [!] Note: {err_msg}")
            executed += 1
        except (subprocess.SubprocessError, OSError) as e:
            print(f"  [!] Error running {name}: {e}")

    print("\n" + "=" * 60)
    print(f" Cleanup complete. {executed} executed, {skipped} skipped.")
    print("=" * 60 + "\n")
    return 0


def register_subparser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser(
        "cleanup",
        aliases=["clean"],
        help="Purge package manager caches (pip, uv, npm, poetry) and trash.",
        description="Purge developer package caches and empty trash to reclaim disk space.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect cleanup targets without deleting files.",
    )
    parser.set_defaults(func=run_cleanup)
