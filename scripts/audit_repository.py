import os
import json
from pathlib import Path

# Repository root (assume script is located in <repo>/scripts)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories and files that must be kept regardless of heuristics
MANDATORY_KEEP_DIRS = {
    "src",
    "story",
    "tests",
    "docs",
    "thread",
    "scripts",
    ".git",
}
MANDATORY_KEEP_FILES = {
    ".gitignore",
    "LICENSE",
    "README.md",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "requirements.txt",
}

# Directories that are considered build/artifact outputs and should be moved to scratch
SCRATCH_DIRS = {
    "build",
    "dist",
    "out",
    "examples",
    "generated",
    "scratch",
    ".venv",
}

# File extensions that are typically generated or temporary
SCRATCH_EXTENSIONS = {
    ".pyc",
    ".log",
    ".tmp",
    ".cache",
    ".egg-info",
    ".so",
    ".o",
    ".obj",
    ".class",
    ".jar",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".pdf",  # often generated docs
}

def classify_path(path: Path) -> tuple[str, str]:
    """Return (classification, reason) for a given repository path.

    Classification choices:
    - KEEP: essential source, docs, tests, config.
    - MOVE_TO_SCRATCH: generated or build artefacts.
    - ARCHIVE: large ancillary assets that are not needed for runtime.
    - DELETE: safe to remove (not used in this conservative audit).
    """
    rel = path.relative_to(REPO_ROOT)
    parts = rel.parts
    name = rel.name

    # .venv and its contents are archived
    if ".venv" in parts:
        return "ARCHIVE", ".venv directory – virtual environment"

    # Mandatory keep files
    if name in MANDATORY_KEEP_FILES:
        return "KEEP", f"Mandatory top‑level file {name}"

    # Mandatory keep directories (any content under them)
    if parts and parts[0] in MANDATORY_KEEP_DIRS:
        return "KEEP", f"Located under mandatory keep directory '{parts[0]}'"

    # Scratch directories – move to scratch
    if parts and parts[0] in SCRATCH_DIRS:
        return "MOVE_TO_SCRATCH", f"Under scratch‑type directory '{parts[0]}'"

    # File extensions that indicate generated artefacts
    if path.is_file() and path.suffix.lower() in SCRATCH_EXTENSIONS:
        return "MOVE_TO_SCRATCH", f"File extension {path.suffix} indicates generated/temporary file"

    # Default conservative choice: KEEP
    return "KEEP", "Conservative default – keep unless clearly generated"

def generate_audit() -> None:
    rows = []
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip hidden VCS directories other than .git (which we keep)
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.git']
        for name in files:
            p = Path(root) / name
            classification, reason = classify_path(p)
            rel_path = str(p.relative_to(REPO_ROOT)).replace(os.sep, "/")
            rows.append((rel_path, classification, reason))

    # Write markdown report
    report_path = REPO_ROOT / "docs" / "REPOSITORY_CLEANUP_AUDIT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Repository Cleanup Audit\n\n")
        f.write("| File Path | Classification | Reason |\n")
        f.write("|-----------|----------------|--------|\n")
        for rel_path, classification, reason in sorted(rows):
            f.write(f"| {rel_path} | {classification} | {reason} |\n")
    # Also emit JSON for programmatic use (optional)
    json_path = REPO_ROOT / "docs" / "repository_cleanup_audit.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump([{"path": r, "classification": c, "reason": rsn} for r, c, rsn in rows], jf, indent=2)

if __name__ == "__main__":
    generate_audit()
