"""
Repo health report.

Pulls basic stats for every public repo owned by TARGET_OWNER, flags repos that
look unhealthy, and writes report.json + report.md.

Docs: https://docs.github.com/en/rest
"""

import os
from datetime import datetime, timedelta
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
    # TODO
    all_repos = []
    page = 1

    while True:
        params = {
            "per_page": 100,
            "page": page,
            "sort": "updated",
            "direction": "desc"
        }

        response = requests.get(f"{API_URL}/users/{owner}/repos", params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}: {response.json().get('message')}")

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

    summed_keys = {'name', 'pushed_at', 'open_issues_count', 'has_pull_requests'}
    summed_repo = {key: repo[key] for key in summed_keys if key in repo}
    return summed_repo


def find_problems(summary):
    """Return a list of human-readable problem strings for one repo.
    An empty list means the repo is healthy."""
    problems = []
    name = summary['name']
    last_push = datetime.strptime(summary['pushed_at'][:10], "%Y-%m-%d")
    #late_date = datetime.now() - timedelta(days = 90)
    date_diff = last_push - datetime.now()
    day_diff = date_diff.days
    if(day_diff > 90):
        problems.append[f"PROBLEM: Last push to repo {name} was more than 90 days ago, work has become stale."]
    problem_count = summary['open_issues_count']
    if(problem_count != 0):
        problems.append[f"PROBLEM: There are {problem_count} problems detected in repo {name}"]
    if(summary['has_pull_requests']):
        problems.append[f"PROBLEM: There are unresolved pull requests for repo {name}"]

def write_reports(results):
    """Write report.json (for machines) and report.md (for humans)."""
    
    pass


def main():
    # TODO: fetch -> summarize -> check -> write
    repos = fetch_repos(OWNER)
    #print(repo)
    for r in repos:
        summed_repo = summarize_repo(r)
        print(summed_repo)
    pass


if __name__ == "__main__":
    main()
