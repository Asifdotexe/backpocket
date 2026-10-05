"""
Universal project scaffolding for modular python repositories
"""

import argparse
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments and setup meaningful defaults

    :returns: A tuple containing Argparser argument namespace and optionally the name of the project
    """
    parser = argparse.ArgumentParser(description="Scaffolding assistant")
    parser.add_argument("project_name", nargs="?", default=None, help="Project name. Defaults to current directory name")
    parser.add_argument("--lib", action="store_true", help="Scaffold python cli like directories src/ for libraries")
    parser.add_argument("--data", action="store_true", help="Scaffold data like directories data/raw, interim and final")
    parser.add_argument("--notebooks", action="store_true", help="Scaffold notesbooks/")
    parser.add_argument("--web", action="store_true", help="Scaffold web/")
    parser.add_argument("--app", action="store_true", help="Scaffold app/ for streamlit like apps and configs")

    args = parser.parse_args()

    # Since all of the options are optional i.e., user can just run the init_repo.py script as is and expect an result
    # to handle that, we need to establish a default, now, since this is for my own usecase the decision of picking
    # the default was on me, hence I went with lib, as that is the most frequent usecase that I have.
    if not any([args.lib, args.data, args.notebooks, args.web, args.app]):
        args.lib = True

    return args


def main() -> None:
    """Entry point for repository init"""
    args = parse_arguments()
    # If the project_name arguement is not populated, we need to impute it with current directory name.
    current_directory_name = Path.cwd().resolve().name
    _ = args.project_name if args.project_name else current_directory_name


if __name__ == "__main__":
    main()
