#!/Users/connorraney/scripts/.venv/bin/python

import os
import subprocess
import sys
from pathlib import Path

try:
    from pathspec import PathSpec
except ImportError:
    print("Missing 'pathspec' library. Install it with: pip install pathspec")
    sys.exit(1)


def count_tokens(text: str) -> int:
    """
    Count tokens in the text. This function tries to use tiktoken for accurate token counting.
    If tiktoken is not available, it falls back to a simple whitespace-based count.
    """
    try:
        import tiktoken
        # Using the encoding for a common model; adjust if needed.
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception:
        # Fallback: approximate token count by splitting on whitespace.
        return len(text.split())


def load_gitignore_patterns(gitignore_path: str):
    """
    Load the .gitignore patterns using pathspec.
    Returns a PathSpec object or None if .gitignore doesn't exist.
    """
    if not os.path.exists(gitignore_path):
        return None

    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore_content = f.read()
    return PathSpec.from_lines("gitwildmatch", gitignore_content.splitlines())


def is_ignored(filepath: str, spec: PathSpec):
    """
    Check if a given filepath is ignored by the .gitignore spec.
    """
    if spec is None:
        return False
    rel_path = os.path.relpath(filepath, start=os.getcwd())
    return spec.match_file(rel_path)


def is_binary_file(filepath: str, check_bytes=1024) -> bool:
    """
    A simple heuristic to check if a file is binary.
    Reads up to check_bytes from the file and checks for non-text characters.
    """
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(check_bytes)
        if b"\0" in chunk:
            return True
        try:
            chunk.decode("utf-8")
        except UnicodeDecodeError:
            return True
        return False
    except Exception:
        return True


def build_file_tree(root: str, spec: PathSpec):
    """
    Recursively walk through the directory, applying .gitignore specs
    and building a nested structure to represent the directory tree.

    Returns a dict representing the tree:
    {
        'folder_name': {
            'sub_folder': {...},
            'file.py': 'FILE',  # or 'BINARY'
            ...
        },
        ...
    }
    """
    tree = {}
    # Folders to skip explicitly, regardless of .gitignore
    skip_dirs = {".git", "__pycache__"}

    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)

        # Skip any directory we don't want, e.g. .git or __pycache__
        if entry in skip_dirs and os.path.isdir(path):
            continue

        # Use .gitignore specs to skip if matched
        if is_ignored(path, spec):
            continue

        if os.path.isdir(path):
            # Recurse
            tree[entry] = build_file_tree(path, spec)
        else:
            # It's a file
            if is_binary_file(path):
                tree[entry] = "BINARY"
            else:
                tree[entry] = "FILE"
    return tree


def render_tree_markdown(tree: dict, prefix: str = "") -> str:
    """
    Render the directory structure as a tree in Markdown.
    """
    lines = []
    for name, value in tree.items():
        if isinstance(value, dict):
            # It's a subfolder
            lines.append(f"{prefix}- **{name}/**")
            lines.append(render_tree_markdown(value, prefix + "  "))
        else:
            # It's a file
            lines.append(f"{prefix}- {name}")
    return "\n".join(lines)


def gather_file_contents(tree: dict, parent_path: str) -> str:
    """
    Recursively traverse the tree structure.
    For 'FILE', read and include its content in a fenced code block.
    For 'BINARY', insert a note indicating it’s binary.
    """
    contents = []
    for name, value in tree.items():
        full_path = os.path.join(parent_path, name)
        if isinstance(value, dict):
            # Recurse into subfolder
            contents.append(gather_file_contents(value, full_path))
        else:
            # It's a file or binary
            if value == "FILE":
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        file_text = f.read()
                except Exception as e:
                    file_text = f"Could not read file: {e}"

                # Pick a language for fenced code blocks based on file extension.
                extension = os.path.splitext(name)[1].lower()
                fence_lang = {
                    ".py": "python",
                    ".js": "javascript",
                    ".ts": "typescript",
                    ".json": "json",
                    ".html": "html",
                    ".css": "css",
                }.get(extension, "")

                contents.append(f"## {full_path}\n")
                contents.append(f"```{fence_lang}")
                contents.append(file_text)
                contents.append("```\n")
            elif value == "BINARY":
                contents.append(f"## {full_path}\n")
                contents.append("_(binary file, not included)_\n")
    return "\n".join(contents)


def main():
    root_dir = os.getcwd()
    gitignore_path = os.path.join(root_dir, ".gitignore")

    spec = load_gitignore_patterns(gitignore_path)
    project_tree = build_file_tree(root_dir, spec)

    # 1) Render the tree structure
    tree_section = "# Project Structure\n\n"
    tree_section += render_tree_markdown(project_tree)

    # 2) Render file contents
    contents_section = "\n\n# File Contents\n\n"
    contents_section += gather_file_contents(project_tree, root_dir)

    final_markdown = tree_section + contents_section

    # Wrap the markdown output in XML <project> tags
    final_markdown = f"<project>\n{final_markdown}\n</project>\n"

    # Count tokens in the final markdown output
    token_count = count_tokens(final_markdown)

    # Copy to clipboard using pbcopy
    subprocess.run(["pbcopy"], input=final_markdown, text=True)

    print("Project has been converted to Markdown (wrapped in <project> tags) and copied to your clipboard.")
    print(f"Total tokens in output: {token_count}")


if __name__ == "__main__":
    main()
