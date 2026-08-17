import argparse
import os
from pathlib import Path

# --- GLOBAL CONFIGURATION & DEFAULTS ---

IGNORED_DIRS = {
    "node_modules",
    ".git",
    ".github",
    ".gradle",
    "target",
    "build",
    "dist",
    "out",
    "bin",
    "obj",
    "coverage",
    "e2e",
    "test-output",
    "__pycache__",
    ".next",
    ".angular",
    ".venv",
    ".idea",
    ".vscode",
    "vendor",
}

IGNORED_EXTENSIONS = {
    # Binaries / Media
    ".pth",
    ".log",
    ".pyc",
    ".class",
    ".jar",
    ".war",
    ".ear",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".obj",
    ".o",
    ".a",
    ".lib",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".ttf",
    ".otf",
    ".wav",
    ".mp3",
    ".mp4",
    # Documentation & Locks
    ".md",
    ".markdown",
    ".txt",
    ".rst",
    ".lock",
    ".resolved",
    # Frontend Build artifacts
    ".map",
    ".min.js",
    ".min.css",
    ".d.ts",
    # IDEs
    ".iml",
    ".project",
    ".classpath",
    ".DS_Store",
}

IGNORED_FILES = {
    ".gitattributes",
    ".editorconfig",
    ".prettierrc",
    "package-lock.json",
    "yarn.lock",
    "tsconfig.json",
    "karma.conf.js",
    "tslint.json",
    "browserslist",
    "polyfills.ts",
    "manifest.yml",
    ".dockerignore",
    ".npmrc",
    ".npmignore",
    ".env.example",
    "mvnw",
    "mvnw.cmd",
    "gradlew",
    "gradlew.bat",
    "Thumbs.db",
}

# Mapping extensions to markdown code block language identifiers
LANG_MAP = {
    ".java": "java",
    ".ts": "typescript",
    ".js": "javascript",
    ".py": "python",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".xml": "xml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sql": "sql",
    ".sh": "bash",
    ".bat": "batch",
    ".properties": "properties",
}


def get_markdown_lang(file_path):
    """Return the language identifier for markdown code blocks based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return LANG_MAP.get(ext, "")


def should_ignore_file(file_path, include_ext=None, exclude_ext=None):
    """
    Determine if a file should be ignored based on extension, filename, or CLI overrides.
    """
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()

    # Normalize user-provided extension overrides
    if include_ext:
        include_ext = {
            e.lower() if e.startswith(".") else f".{e.lower()}" for e in include_ext
        }
        if file_ext in include_ext:
            return False

    if exclude_ext:
        exclude_ext = {
            e.lower() if e.startswith(".") else f".{e.lower()}" for e in exclude_ext
        }
        if file_ext in exclude_ext:
            return True

    # Check hardcoded ignores
    return (file_ext in IGNORED_EXTENSIONS) or (file_name in IGNORED_FILES)


def should_ignore_directory(dir_name):
    """Check if a directory should be ignored."""
    return dir_name in IGNORED_DIRS


def is_binary_file(file_path):
    """Fast check to see if a file is binary by reading its first 1024 bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\0" in chunk  # Null bytes usually indicate binary files
    except Exception:
        return True


def generate_tree_structure(
    directory_path, prefix="", is_last=True, max_depth=10, current_depth=0
):
    """Generate ASCII tree structure of the directory."""
    if current_depth > max_depth:
        return ""

    tree_str = ""
    dir_name = os.path.basename(directory_path) or directory_path

    if current_depth == 0:
        tree_str += f"{dir_name}/\n"
    else:
        connector = "└── " if is_last else "├── "
        tree_str += f"{prefix}{connector}{dir_name}/\n"

    next_prefix = prefix + ("    " if is_last else "│   ")

    try:
        items = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                if not should_ignore_directory(item):
                    items.append(("dir", item, item_path))
            elif not should_ignore_file(item_path):
                items.append(("file", item, item_path))

        items.sort(key=lambda x: (x[0] == "file", x[1].lower()))

        for i, (item_type, item_name, item_path) in enumerate(items):
            is_last_item = i == len(items) - 1

            if item_type == "dir":
                tree_str += generate_tree_structure(
                    item_path, next_prefix, is_last_item, max_depth, current_depth + 1
                )
            else:
                connector = "└── " if is_last_item else "├── "
                tree_str += f"{next_prefix}{connector}{item_name}\n"

    except PermissionError:
        tree_str += f"{next_prefix}└── [Permission Denied]\n"
    except Exception as e:
        tree_str += f"{next_prefix}└── [Error: {e}]\n"

    return tree_str


def process_directory(
    directory_path,
    output_file,
    show_tree=True,
    max_tree_depth=10,
    include_ext=None,
    exclude_ext=None,
    max_file_size_kb=500,
):
    """
    Process all relevant files in the directory, writing contents to output file in Markdown.
    """
    try:
        abs_dir_path = os.path.abspath(directory_path)
        abs_output_file = os.path.abspath(output_file)
        print(f"Processing directory: {abs_dir_path}")

        file_count = 0
        skipped_count = 0
        total_chars = 0

        with open(abs_output_file, "w", encoding="utf-8", errors="replace") as out_f:
            out_f.write(f"# Repository Context: `{os.path.basename(abs_dir_path)}`\n\n")

            if show_tree:
                print("Generating directory tree structure...")
                out_f.write("## Directory Structure\n```text\n")
                tree_structure = generate_tree_structure(
                    abs_dir_path, max_depth=max_tree_depth
                )
                out_f.write(tree_structure)
                out_f.write("```\n\n")

            out_f.write("## File Contents\n\n")

            # Efficient directory walk with pruning
            for root, dirs, files in os.walk(abs_dir_path):
                # PRUNING: Modifying `dirs` in-place prevents walking ignored folders (e.g. node_modules, target)
                dirs[:] = [d for d in dirs if not should_ignore_directory(d)]

                for file in files:
                    file_path = os.path.join(root, file)

                    if os.path.abspath(file_path) == abs_output_file:
                        continue

                    if should_ignore_file(
                        file_path, include_ext=include_ext, exclude_ext=exclude_ext
                    ):
                        skipped_count += 1
                        continue

                    # Skip files larger than specified size limit
                    if os.path.getsize(file_path) > max_file_size_kb * 1024:
                        print(
                            f"Skipped (Exceeds {max_file_size_kb}KB): {os.path.relpath(file_path, abs_dir_path)}"
                        )
                        skipped_count += 1
                        continue

                    # Check for undetected binaries
                    if is_binary_file(file_path):
                        skipped_count += 1
                        continue

                    try:
                        # Clean, clean relative path display
                        rel_path = os.path.relpath(file_path, abs_dir_path).replace(
                            "\\", "/"
                        )
                        lang = get_markdown_lang(file_path)

                        with open(
                            file_path, "r", encoding="utf-8", errors="replace"
                        ) as f:
                            content = f.read()

                        # Markdown formatted output for easier LLM parsing
                        out_f.write(f"### `{rel_path}`\n")
                        out_f.write(f"```{lang}\n")
                        out_f.write(content)
                        out_f.write("\n```\n\n")

                        file_count += 1
                        total_chars += len(content)
                        print(f"Processed: {rel_path}")

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

            # Summary footer
            estimated_tokens = total_chars // 4
            out_f.write("---\n")
            out_f.write(
                f"**Summary:** Processed {file_count} files | Skipped {skipped_count} files | Approx. Tokens: ~{estimated_tokens:,}\n"
            )

            print("\n" + "=" * 40)
            print(f"Completed successfully!")
            print(f"Files Processed: {file_count}")
            print(f"Files Skipped:   {skipped_count}")
            print(f"Est. Tokens:     ~{estimated_tokens:,}")
            print(f"Output saved to: {abs_output_file}")
            print("=" * 40)

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate code context into a single structured Markdown file for LLMs."
    )
    parser.add_argument("directory", help="Path to the directory to process")
    parser.add_argument(
        "-o",
        "--output",
        default="directory_contents.md",
        help="Output file name (default: directory_contents.md)",
    )
    parser.add_argument(
        "--include-ext",
        nargs="+",
        help="Force include specific extensions (e.g. --include-ext md txt log)",
    )
    parser.add_argument(
        "--exclude-ext",
        nargs="+",
        help="Force exclude specific extensions (e.g. --exclude-ext css scss)",
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Skip generating the directory tree structure",
    )
    parser.add_argument(
        "--tree-depth",
        type=int,
        default=10,
        help="Maximum tree depth (default: 10)",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=500,
        help="Maximum file size in KB to process (default: 500KB)",
    )

    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    output = args.output

    if not os.path.isabs(output):
        output = os.path.join(directory, output)

    process_directory(
        directory_path=directory,
        output_file=output,
        show_tree=not args.no_tree,
        max_tree_depth=args.tree_depth,
        include_ext=args.include_ext,
        exclude_ext=args.exclude_ext,
        max_file_size_kb=args.max_size,
    )


if __name__ == "__main__":
    main()