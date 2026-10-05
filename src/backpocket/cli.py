"""
backpocket CLI entrypoint.
Dispatches subcommands to modular command handlers in backpocket.commands.
"""

import argparse
import sys

from backpocket import __version__
from backpocket.commands import cleanup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="backpocket",
        description="Essential developer utilities and automation kept in your backpocket.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="available commands",
        metavar="<command>",
    )

    # Register active commands
    cleanup.register_subparser(subparsers)

    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
