"""Post-build: generate build-info.json in dist directory."""
import json
import subprocess
from pathlib import Path

DIST_DIR = Path(__file__).parent.parent / "ui-vben" / "apps" / "web-antd" / "dist"
REPO_ROOT = Path(__file__).parent.parent

def get_git_info():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT).decode().strip()
        return commit, branch
    except Exception:
        return "unknown", "unknown"

if __name__ == "__main__":
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    commit, branch = get_git_info()
    info = {
        "build_time": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "git_commit": commit,
        "git_branch": branch,
        "version": "0.1.0",
    }
    info_path = DIST_DIR / "build-info.json"
    info_path.write_text(json.dumps(info, indent=2))
    print(f"Generated {info_path}")
