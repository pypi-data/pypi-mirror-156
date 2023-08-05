# type: ignore[attr-defined]
"""
Demonstrates how to display a tree of files / directories with the Tree renderable.
"""

from pathlib import Path

from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

ICONS = {
    ".py": "🐍 ",
    ".md": "📑 ",
    ".txt": "📄 ",
    ".toml": "📝 ",
    ".gitignore": "📄 ",
}


def walk_directory(directory: Path, tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    paths = sorted(
        Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.stylize(f"link file://{path}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = ICONS.get(path.suffix, "")
            tree.add(Text(icon) + text_filename)
