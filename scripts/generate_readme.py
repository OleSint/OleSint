#!/usr/bin/env python3
"""
Holt alle öffentlichen, nicht geforkten, nicht archivierten Repos von OleSint
und schreibt eine aktuelle Projekt-Tabelle zwischen die Marker
<!-- REPOS:START --> und <!-- REPOS:END --> in README.md.

Wird von .github/workflows/update-readme.yml automatisch (nächtlich) ausgeführt.
Lokal testen: python3 scripts/generate_readme.py
"""

import json
import os
import re
import urllib.request

USERNAME = "OleSint"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")


def fetch_repos():
    req = urllib.request.Request(API_URL, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)

    repos = [
        r for r in data
        if not r["fork"]
        and not r["private"]
        and not r["archived"]
        and r["name"].lower() != USERNAME.lower()  # Profil-Repo selbst ausschließen
    ]
    repos.sort(key=lambda r: r["stargazers_count"], reverse=True)
    return repos


def build_table(repos):
    if not repos:
        return "_Noch keine öffentlichen Repos._"

    lines = ["| Project | Description | ⭐ |", "|---|---|---|"]
    for r in repos:
        desc = (r["description"] or "").replace("|", "-").strip()
        lines.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {r['stargazers_count']} |")
    return "\n".join(lines)


def update_readme(table):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"(<!-- REPOS:START -->)(.*?)(<!-- REPOS:END -->)",
        lambda m: f"{m.group(1)}\n{table}\n{m.group(3)}",
        content,
        flags=re.DOTALL,
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    repos = fetch_repos()
    table = build_table(repos)
    update_readme(table)
    print(f"README aktualisiert mit {len(repos)} Repos.")
