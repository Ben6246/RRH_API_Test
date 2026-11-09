"""
Repo health report.

Pulls basic stats for every public repo owned by TARGET_OWNER, flags repos that
look unhealthy, and writes report.json + report.md.

Docs: https://docs.github.com/en/rest
"""

import os
import json
from datetime import datetime, timedelta, timezone
import requests

API_URL = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("TARGET_OWNER", "Ben6246")

# Thresholds for what counts as "unhealthy" -- tune these however you like.
STALE_DAYS = 90
MAX_OPEN_ISSUES = 10

def fetch_repos(owner):
    """Return a list of repo dicts for the owner.

    Endpoint: GET /users/{username}/repos  (or /orgs/{org}/repos for an org)
    """
    all_repos = []
    page = 1

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    while True:

        params = {
            "per_page": 100,
            "page": page,
            "sort": "updated",
            "direction": "desc"
        }

        response = requests.get(f"{API_URL}/users/{owner}/repos", headers=headers, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Error: {response.status_code}: {response.json().get('message')}")
            raise SystemExit(1)
        
        repos = response.json()

        if not repos:
            break

        all_repos.extend(repos)

        if len(repos) < 100:
            break

        page+=1

    return all_repos


def summarize_repo(repo):
    """Turn one raw repo dict from the API into a small dict with only the
    fields you care about (name, stars, open issues, last push, etc.)."""

    summed_keys = ('name', 'pushed_at', 'open_issues_count')
    summed_repo = {key: repo[key] for key in summed_keys if key in repo}
    return summed_repo


def find_problems(summary):
    """Return a list of human-readable problem strings for one repo.
    An empty list means the repo is healthy."""
    problems = []
    name = summary['name']
    last_push = datetime.strptime(summary['pushed_at'][:10], "%Y-%m-%d")
    date_diff = datetime.now() - last_push
    day_diff = date_diff.days
    if day_diff > STALE_DAYS:
        problems.append(f"{name}: no pushes in {day_diff} days (threshold: {STALE_DAYS})")
    open_count = summary['open_issues_count']
    if open_count > MAX_OPEN_ISSUES:
        problems.append(
            f"{name} has {open_count} open issues/PRs (threshold: {MAX_OPEN_ISSUES})"
        )

    return problems

def write_reports(results):
    """Write report.json (for machines) and report.md (for humans)."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    unhealthy = [r for r in results if r["problems"]]
    report = {
        "owner": OWNER,
        "generated_at": generated_at,
        "total_repos": len(results),
        "unhealthy_repos": len(unhealthy),
        "results": results,
    }
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)

    # --- Markdown: a readable summary that GitHub renders nicely ---
    lines = [
        f"# Repo Health Report: {OWNER}",
        "",
        f"_Generated {generated_at}_",
        "",
        f"**{len(unhealthy)} of {len(results)} repos need attention.**",
        "",
    ]

    if unhealthy:
        lines.append("## Needs attention")
        lines.append("")
        for r in unhealthy:
            lines.append(f"### {r['repo']}")
            for problem in r["problems"]:
                lines.append(f"- {problem}")
            lines.append("")

    healthy = [r["repo"] for r in results if not r["problems"]]
    if healthy:
        lines.append("## Healthy")
        lines.append("")
        for name in healthy:
            lines.append(f"- {name}")
        lines.append("")

    with open("report.md", "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote report.json and report.md ({len(unhealthy)} unhealthy of {len(results)})")


def main():
    repos = fetch_repos(OWNER)
    results = []
    for r in repos:
        summed_repo = summarize_repo(r)
        problems = find_problems(summed_repo)
        results.append({"repo": summed_repo["name"], "problems": problems})
    write_reports(results)

if __name__ == "__main__":
    main()