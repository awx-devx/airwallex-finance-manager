#!/usr/bin/env python3
"""Merge this pack's Hermes fragment into ~/.hermes/config.yaml and .env."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml


def _load_yaml(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size == 0:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def merge_config(existing: dict, repo_root: Path) -> dict:
    root = str(repo_root)
    skills = existing.setdefault("skills", {})
    if not isinstance(skills, dict):
        skills = {}
        existing["skills"] = skills
    dirs = skills.setdefault("external_dirs", [])
    if not isinstance(dirs, list):
        dirs = []
        skills["external_dirs"] = dirs
    skill_path = f"{root}/skills"
    placeholders = {
        "${FINANCE_MANAGER_ROOT}/skills",
        "$FINANCE_MANAGER_ROOT/skills",
        skill_path,
    }
    if not any(str(item) in placeholders or str(item) == skill_path for item in dirs):
        dirs.append("${FINANCE_MANAGER_ROOT}/skills")

    servers = existing.setdefault("mcp_servers", {})
    if not isinstance(servers, dict):
        servers = {}
        existing["mcp_servers"] = servers

    servers.setdefault(
        "airwallex",
        {
            "url": "https://mcp.airwallex.com/mcp",
            "auth": "oauth",
            "enabled": True,
        },
    )
    servers["finance-manager"] = {
        "command": "uv",
        "args": [
            "run",
            "--directory",
            "${FINANCE_MANAGER_ROOT}/mcp/finance-manager",
            "python",
            "-m",
            "finance_manager",
        ],
        "env": {
            "FINANCE_MANAGER_KNOWLEDGE_DIR": "${FINANCE_MANAGER_ROOT}/knowledge",
        },
        "enabled": True,
        "tools": {"resources": False, "prompts": False},
    }
    return existing


def upsert_env(env_path: Path, values: dict[str, str]) -> list[str]:
    lines: list[str] = []
    if env_path.is_file():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    keys_present = set()
    changed: list[str] = []
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            out.append(line)
            continue
        key, _, current = line.partition("=")
        key = key.strip()
        keys_present.add(key)
        if key in values and not current.strip():
            out.append(f"{key}={values[key]}")
            changed.append(key)
        else:
            out.append(line)
    for key, value in values.items():
        if key not in keys_present:
            out.append(f"{key}={value}")
            changed.append(key)
    env_path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(out).rstrip() + "\n"
    env_path.write_text(text, encoding="utf-8")
    return changed


def copy_soul(repo_soul: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    incoming = repo_soul.read_text(encoding="utf-8")
    if dest.exists():
        current = dest.read_text(encoding="utf-8")
        if current == incoming:
            return f"already current: {dest}"
        backup = dest.with_name("SOUL.pre-finance-manager.md")
        if not backup.exists():
            backup.write_text(current, encoding="utf-8")
            dest.write_text(incoming, encoding="utf-8")
            return f"wrote {dest} (previous soul backed up to {backup})"
        dest.write_text(incoming, encoding="utf-8")
        return f"wrote {dest} (left existing {backup} in place)"
    dest.write_text(incoming, encoding="utf-8")
    return f"wrote {dest}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--hermes-home",
        type=Path,
        default=Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")),
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    hermes = args.hermes_home.expanduser()
    hermes.mkdir(parents=True, exist_ok=True)

    config_path = hermes / "config.yaml"
    existing = _load_yaml(config_path)
    merged = merge_config(existing, repo_root)
    config_path.write_text(
        yaml.safe_dump(merged, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )

    env_changes = upsert_env(
        hermes / ".env",
        {
            "FINANCE_MANAGER_ROOT": str(repo_root),
            "TELEGRAM_BOT_TOKEN": "",
            "TELEGRAM_ALLOWED_USERS": "",
        },
    )
    soul_msg = copy_soul(repo_root / "hermes" / "SOUL.md", hermes / "SOUL.md")

    print(f"Updated {config_path}")
    print(f"Env keys touched: {', '.join(env_changes) or 'none'}")
    print(soul_msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
