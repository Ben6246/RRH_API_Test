# Repo Health Report

A scheduled GitHub Action that checks the health of a user's or organization's
repositories through the GitHub REST API and publishes a daily report.

<!-- TODO: one or two sentences in your own words on why you built this. -->

## What it checks

<!-- TODO: list each check and its threshold, e.g. "No pushes in 90+ days". -->

## How it works

1. A GitHub Actions workflow runs every day (and on demand from the Actions tab).
2. `repo_health.py` calls the GitHub API, using the workflow's built-in token.
3. It flags repos that look unhealthy and writes `report.json` and `report.md`.
4. The workflow commits the updated report back to this repo.

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export GITHUB_TOKEN=$(gh auth token)   # or paste a personal access token
export TARGET_OWNER=your-username
python repo_health.py
```

## Latest report

See [report.md](report.md).

## What I'd add next

<!-- TODO: e.g. pagination, Slack/Teams alert on new problems, Dockerfile, tests. -->
