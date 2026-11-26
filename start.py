"""Prepare a copied project for local development.

Run this script from the repository root: ``python start.py``.
It deliberately creates a fresh Git repository, so do not run it in a
repository whose Git history you want to keep.
"""

from __future__ import annotations

import os
import re
import secrets
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DOCKER_DIR = ROOT_DIR / "docker"
APPLICATION_DIR = ROOT_DIR / "application"


def update_project_name() -> None:
    """Set the package name to the directory where the script was started."""
    pyproject_path = ROOT_DIR / "pyproject.toml"
    project_name = Path.cwd().name
    content = pyproject_path.read_text(encoding="utf-8")

    updated_content, replacements = re.subn(
        r'(?ms)(^\[project\]\s*$.*?^name\s*=\s*)"[^"]*"',
        rf'\g<1>"{project_name}"',
        content,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError("Cannot find [project].name in pyproject.toml.")

    if updated_content != content:
        pyproject_path.write_text(updated_content, encoding="utf-8")
        print(f"Set project name to {project_name}")


def write_if_missing(path: Path, content: str) -> None:
    """Create a configuration file once without replacing user settings."""
    if path.exists():
        print(f"Keeping existing {path.relative_to(ROOT_DIR)}")
        return

    path.write_text(content, encoding="utf-8")
    print(f"Created {path.relative_to(ROOT_DIR)}")


def read_env_value(path: Path, name: str) -> str | None:
    """Read a simple KEY=value entry from an existing local env file."""
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key == name:
            return value
    return None


def run(*command: str) -> None:
    environment = os.environ | {"UV_CACHE_DIR": str(ROOT_DIR / ".uv-cache")}
    environment.pop("VIRTUAL_ENV", None)
    subprocess.run(command, cwd=ROOT_DIR, check=True, env=environment)


def main() -> None:
    if not (ROOT_DIR / "pyproject.toml").is_file():
        raise RuntimeError("Run start.py from the root of the copied project.")

    update_project_name()
    DOCKER_DIR.mkdir(exist_ok=True)
    APPLICATION_DIR.mkdir(exist_ok=True)

    docker_env = DOCKER_DIR / ".env"
    postgres_password = read_env_value(docker_env, "POSTGRES_PASSWORD") or secrets.token_urlsafe(24)
    redis_password = read_env_value(docker_env, "REDIS_PASSWORD") or secrets.token_urlsafe(24)

    write_if_missing(
        docker_env,
        "\n".join(
            (
                "POSTGRES_DB=app",
                "POSTGRES_USER=app",
                f"POSTGRES_PASSWORD={postgres_password}",
                "RABBITMQ_DEFAULT_USER=app",
                f"RABBITMQ_DEFAULT_PASS={secrets.token_urlsafe(24)}",
                f"REDIS_PASSWORD={redis_password}",
                "",
            )
        ),
    )
    write_if_missing(
        APPLICATION_DIR / ".env",
        "\n".join(
            (
                "APP_ENV=development",
                "POSTGRES_HOST=pg_db",
                "POSTGRES_PORT=5432",
                "POSTGRES_DB=app",
                "POSTGRES_USER=app",
                f"POSTGRES_PASSWORD={postgres_password}",
                "REDIS_HOST=rediska",
                "REDIS_PORT=6379",
                f"REDIS_PASSWORD={redis_password}",
                "RABBITMQ_HOST=rabbitmq",
                "RABBITMQ_PORT=5672",
                "",
            )
        ),
    )
    write_if_missing(
        DOCKER_DIR / "users.acl",
        f"user default on >{redis_password} ~* &* +@all\n",
    )

    git_dir = ROOT_DIR / ".git"
    if git_dir.exists():
        try:
            shutil.rmtree(git_dir)
        except OSError as error:
            raise RuntimeError(
                f"Cannot remove {git_dir}. Close programs using this repository "
                "and try again."
            ) from error
        print("Removed previous Git metadata")
    run("git", "init")
    run("uv", "sync")
    print("Project is ready. Start services with: docker compose -f docker/docker-compose.yaml up --build")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
