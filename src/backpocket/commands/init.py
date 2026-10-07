"""
Universal project scaffolding engine for modular Python repositories.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def slugify_package_name(raw_name: str) -> str:
    """Normalize arbitrary project naming strings into valid Python identifiers.

    Standard build systems (PEP 508 / Hatchling) enforce strict identifier
    boundaries. Hyphens, dots, and spaces are transformed to underscores, and
    leading invalid characters are stripped or prefixed to avoid dynamic import
    failures.

    :param raw_name: User-provided project name or directory name.
    """
    clean_slug = re.sub(r"[-.\s]+", "_", raw_name.strip()).lower()
    clean_slug = re.sub(r"[^\w]", "", clean_slug)
    if clean_slug and clean_slug[0].isdigit():
        clean_slug = f"pkg_{clean_slug}"
    return clean_slug or "my_project"


class ProjectScaffolder:
    """Manages the idempotent file layout generation across target repositories."""

    def __init__(self, root: Path, project_name: str) -> None:
        """Initialize the scaffolder context.

        :param root: Root directory where scaffolding occurs.
        :param project_name: Human-friendly or directory name for the project.
        """
        self.root = root
        self.project_name = project_name
        self.package_slug = slugify_package_name(project_name)

    def write_safe(self, rel_path: Path | str, content: str) -> None:
        """Create target parent directories and write file content without overwrites.

        Existing files are preserved to make subsequent command invocations
        (e.g., adding --data to an existing --lib repo) strictly additive and safe.

        :param rel_path: File path relative to project root.
        :param content: Template content to write.
        """
        dest = self.root / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_text(content.lstrip("\n"), encoding="utf-8")

    def ensure_dir(self, rel_path: Path | str, keep: bool = True) -> None:
        """Ensure a directory exists and optionally inject a .gitkeep file.

        Git ignores truly empty directories. Placing a zero-byte .gitkeep
        preserves targeted repository skeletons in VCS before real artifacts land.

        :param rel_path: Target directory path relative to project root.
        :param keep: Whether to track the directory using a .gitkeep placeholder.
        """
        target = self.root / rel_path
        target.mkdir(parents=True, exist_ok=True)
        if keep:
            (target / ".gitkeep").touch(exist_ok=True)

    def scaffold_core(self) -> None:
        """Assemble the non-negotiable core invariants present in every repo."""
        pre_commit = (
            "repos:\n"
            "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
            "    rev: v5.0.0\n"
            "    hooks:\n"
            "      - id: trailing-whitespace\n"
            "      - id: end-of-file-fixer\n"
            "      - id: check-yaml\n"
            "      - id: check-added-large-files\n"
            "        args: ['--maxkb=1024']\n\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: ruff-check\n"
            "        name: ruff check\n"
            "        entry: uv run --no-sync ruff check\n"
            "        language: system\n"
            "        types: [python]\n\n"
            "      - id: ruff-format\n"
            "        name: ruff format\n"
            "        entry: uv run ruff format\n"
            "        language: system\n"
            "        types: [python]\n"
        )

        pyproject = (
            f"[project]\n"
            f'name = "{self.package_slug}"\n'
            f'version = "0.1.0"\n'
            f'description = "Automated workspace for {self.project_name}"\n'
            f'readme = "README.md"\n'
            f'requires-python = ">=3.12"\n'
            f"dependencies = []\n\n"
            f"[project.scripts]\n"
            f'{self.package_slug} = "{self.package_slug}.cli:main"\n\n'
            f"[build-system]\n"
            f'requires = ["hatchling"]\n'
            f'build-backend = "hatchling.build"\n\n'
            f"[dependency-groups]\n"
            f"dev = [\n"
            f'    "ruff>=0.16.9",\n'
            f'    "pytest>=8.0.0",\n'
            f"]\n\n"
            f"[tool.ruff]\n"
            f"line-length = 100\n"
            f'target-version = "py312"\n\n'
            f"[tool.ruff.lint]\n"
            f'select = ["E", "F", "I", "W", "UP"]\n'
            f'ignore = ["E501"]\n'
        )

        ci_workflow = (
            "name: CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, master]\n"
            "  pull_request:\n"
            "    branches: [main, master]\n\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Install uv\n"
            "        uses: astral-sh/setup-uv@v3\n"
            "        with:\n"
            "          enable-cache: true\n"
            "      - name: Set up Python\n"
            "        run: uv python install 3.12\n"
            "      - name: Run linter and formatter checks\n"
            "        run: |\n"
            "          uv run ruff check .\n"
            "          uv run ruff format --check .\n"
            "      - name: Execute test suite\n"
            "        run: uv run pytest\n"
        )

        readme = (
            f"# {self.project_name}\n\n"
            f"Repository initialized via modular scaffolding.\n\n"
            f"## Development Setup\n\n"
            f"```bash\n"
            f"# Sync virtualenv and dependencies via uv\n"
            f"uv sync\n\n"
            f"# Run quality checks\n"
            f"uv run ruff check .\n"
            f"uv run pytest\n"
            f"```\n"
        )

        arch_doc = (
            f"# Architecture & Design: {self.project_name}\n\n"
            f"## Overview\n"
            f"Document the core modules, external dependencies, and system boundaries here.\n"
        )

        dev_bat = (
            "@echo off\n"
            "echo [DEV] Running quality checks and test suite...\n"
            "uv run ruff check .\n"
            "uv run pytest\n"
        )

        self.write_safe(".pre-commit-config.yaml", pre_commit)
        self.write_safe("pyproject.toml", pyproject)
        self.write_safe("README.md", readme)
        self.write_safe(".github/workflows/ci.yml", ci_workflow)
        self.write_safe("docs/ARCHITECTURE.md", arch_doc)
        self.write_safe("scripts/dev.bat", dev_bat)
        self.write_safe("tests/__init__.py", "")

    def scaffold_lib(self) -> None:
        """Inject src-layout package boundaries and CLI dispatch logic."""
        pkg_root = Path("src") / self.package_slug
        init_file = f'"""Package entry point for {self.package_slug}."""\n\n__version__ = "0.1.0"\n'
        cli_file = (
            f'"""Command-line interface entry point for {self.package_slug}."""\n\n'
            f"import sys\n\n\n"
            f"def main() -> None:\n"
            f'    """Parse arguments and handle process dispatch."""\n'
            f'    print("Running {self.package_slug} CLI...")\n'
            f"    sys.exit(0)\n\n\n"
            f'if __name__ == "__main__":\n'
            f"    main()\n"
        )

        self.ensure_dir(pkg_root / "core")
        self.write_safe(pkg_root / "__init__.py", init_file)
        self.write_safe(pkg_root / "py.typed", "")
        self.write_safe(pkg_root / "core/__init__.py", "")
        self.write_safe(pkg_root / "cli.py", cli_file)

        test_cli = (
            f"from {self.package_slug}.cli import main\n\n\n"
            f"def test_cli_importable() -> None:\n"
            f"    assert callable(main)\n"
        )
        self.write_safe("tests/test_cli.py", test_cli)

    def scaffold_data(self) -> None:
        """Inject data tier layout with strict git-exclusion boundaries."""
        for sub in ("raw", "interim", "processed"):
            self.ensure_dir(Path("data") / sub, keep=True)

        data_gitignore = (
            "# Ignore all contents in this folder\n"
            "*\n"
            "# Preserve tracking metadata and layout structure\n"
            "!.gitignore\n"
            "!*/\n"
            "!**/.gitkeep\n"
        )
        self.write_safe("data/.gitignore", data_gitignore)

    def scaffold_notebooks(self) -> None:
        """Create an isolated exploratory notebook directory."""
        self.ensure_dir(Path("notebooks"), keep=True)

    def scaffold_web(self) -> None:
        """Inject client assets isolated under web/ to prevent root clutter."""
        html_content = (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '    <meta charset="UTF-8">\n'
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f"    <title>{self.project_name}</title>\n"
            '    <link rel="stylesheet" href="style.css">\n'
            "</head>\n"
            "<body>\n"
            f"    <main><h1>{self.project_name}</h1></main>\n"
            '    <script src="main.js"></script>\n'
            "</body>\n"
            "</html>\n"
        )
        css_content = (
            "body {\n    margin: 0;\n    font-family: system-ui, sans-serif;\n}\n"
        )
        js_content = 'console.log("Interface initialized.");\n'

        self.write_safe("web/index.html", html_content)
        self.write_safe("web/style.css", css_content)
        self.write_safe("web/main.js", js_content)

    def scaffold_app(self) -> None:
        """Inject Streamlit and interactive app assets."""
        streamlit_config = '[server]\nheadless = true\n\n[theme]\nbase = "dark"\n'
        app_entry = (
            '"""Streamlit UI dashboard entry point."""\n\n'
            "import streamlit as st\n\n"
            f'st.set_page_config(page_title="{self.project_name}", layout="wide")\n'
            f'st.title("{self.project_name}")\n'
            'st.write("Dashboard ready.")\n'
        )
        self.write_safe(".streamlit/config.toml", streamlit_config)
        self.write_safe("app.py", app_entry)


def run_init(args: argparse.Namespace) -> int:
    """Entry point orchestration for repo scaffolding."""
    if not any([args.lib, args.data, args.notebooks, args.web, args.app]):
        args.lib = True

    target_dir = Path.cwd()
    project_name = args.name if args.name else target_dir.resolve().name
    scaffolder = ProjectScaffolder(root=target_dir, project_name=project_name)

    scaffolder.scaffold_core()

    if args.lib:
        scaffolder.scaffold_lib()
    if args.data:
        scaffolder.scaffold_data()
    if args.notebooks:
        scaffolder.scaffold_notebooks()
    if args.web:
        scaffolder.scaffold_web()
    if args.app:
        scaffolder.scaffold_app()

    print(f"Workspace configured for: {project_name}")
    return 0


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'init' subparser on backpocket CLI."""
    parser = subparsers.add_parser(
        "init",
        aliases=["scaffold"],
        help="Fast, additive, non-destructive project structure scaffolder.",
        description="Scaffold standardized project directories, configs, and boilerplate.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default=None,
        help="Project name. Defaults to current directory name if omitted.",
    )
    parser.add_argument(
        "--lib", action="store_true", help="Scaffold Python src/ library and CLI."
    )
    parser.add_argument(
        "--data", action="store_true", help="Scaffold data/raw, interim, processed."
    )
    parser.add_argument(
        "--notebooks", action="store_true", help="Scaffold notebooks/ scratchpad."
    )
    parser.add_argument(
        "--web", action="store_true", help="Scaffold web/ interface assets."
    )
    parser.add_argument(
        "--app", action="store_true", help="Scaffold Streamlit app.py and configs."
    )
    parser.set_defaults(func=run_init)
