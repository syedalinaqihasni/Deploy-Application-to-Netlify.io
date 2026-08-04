#!/usr/bin/env python3

from pathlib import Path
import shutil
import subprocess

repo = Path.cwd()

if not (repo / ".git").exists():
    raise SystemExit("Current directory is not a Git repository.")

LOCK_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lock",
    "bun.lockb",
    "Cargo.lock",
    "composer.lock",
    "Gemfile.lock",
    "Podfile.lock",
    "flake.lock",
}

def run(cmd, check=True):
    return subprocess.run(cmd, cwd=repo, check=check)

# Get all local branches
branches = subprocess.check_output(
    ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"],
    cwd=repo,
    text=True,
).splitlines()

for branch in branches:
    print(f"\n=== {branch} ===")

    run(["git", "checkout", branch])

    changed = False

    # Remove .bolt directory
    bolt = repo / ".bolt"
    if bolt.exists():
        shutil.rmtree(bolt)
        print("Removed .bolt/")
        changed = True

    # Remove lock files
    for f in repo.rglob("*"):
        if not f.is_file():
            continue

        name = f.name

        if (
            name in LOCK_FILES
            or name.endswith(".lock")
            or ".lock." in name
        ):
            try:
                f.unlink()
                print(f"Removed {f.relative_to(repo)}")
                changed = True
            except Exception:
                pass

    if not changed:
        print("No changes.")
        continue

    run(["git", "add", "-A"])

    # Commit only if there are staged changes
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo).returncode != 0:
        run(["git", "commit", "-m", "Remove .bolt directory and lock files"])

    # Force push current branch
    run(["git", "push", "--force", "origin", branch])

print("\nDone.")