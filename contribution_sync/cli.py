#!/usr/bin/env python3
import argparse
import datetime
import logging
import os
from datetime import datetime as dt
from typing import Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Load environment variables from .env file.
from dotenv import load_dotenv

load_dotenv()
logging.info("Loaded environment variables from .env file")

### PART 1: Contributions Parsing ###


def get_contributions(username: str, year: int) -> Dict[str, int]:
    """
    Get contributions for a given GitHub username and year.
    Fetches the public contributions page and parses the HTML to return a
    dictionary mapping date (YYYY-MM-DD) to contribution count (int).

    This version looks for <td class="ContributionCalendar-day"> elements and
    extracts the contribution level from the "data-level" attribute.
    """
    from_date = f"{year}-01-01"
    to_date = f"{year}-12-31"
    url = f"https://github.com/users/{username}/contributions?from={from_date}&to={to_date}"
    logging.info("Fetching contributions from URL: %s", url)
    r: requests.Response = requests.get(url)
    if r.status_code != 200:
        logging.error(
            "Failed to fetch contributions for %s: HTTP %s", username, r.status_code
        )
        r.raise_for_status()
    html: str = r.text
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    contributions: Dict[str, int] = {}
    # The contributions page contains many <td class="ContributionCalendar-day" ...> tags.
    for td in soup.find_all("td", {"class": "ContributionCalendar-day"}):
        date: Optional[str] = td.get("data-date")
        count: Optional[str] = td.get("data-level")
        if date and count:
            try:
                contributions[date] = int(count)
            except ValueError:
                contributions[date] = 0
    logging.info("Parsed %d days of contributions for %s", len(contributions), username)
    return contributions


### PART 2: GitHub API Helpers ###


def get_latest_commit(owner: str, repo: str, branch: str, token: str) -> str:
    """
    Retrieves the latest commit SHA on the given branch using the GitHub API.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{branch}"
    headers = {"Authorization": f"token {token}"}
    r: requests.Response = requests.get(url, headers=headers)
    r.raise_for_status()
    data: Dict[str, Any] = r.json()
    commit_sha: str = data["object"]["sha"]
    logging.info("Latest commit on %s/%s is %s", repo, branch, commit_sha)
    return commit_sha


def get_commit_tree(owner: str, repo: str, commit_sha: str, token: str) -> str:
    """
    Retrieves the tree SHA for a given commit.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/commits/{commit_sha}"
    headers = {"Authorization": f"token {token}"}
    r: requests.Response = requests.get(url, headers=headers)
    r.raise_for_status()
    data: Dict[str, Any] = r.json()
    tree_sha: str = data["tree"]["sha"]
    logging.info("Tree for commit %s is %s", commit_sha, tree_sha)
    return tree_sha


def create_commit(
    owner: str,
    repo: str,
    message: str,
    tree_sha: str,
    parent_sha: str,
    commit_date: str,
    author_name: str,
    author_email: str,
    token: str,
) -> str:
    """
    Creates a new commit (with no file changes) using the GitHub API.
    The commit uses the same tree as the parent commit to be an 'empty commit',
    and sets the commit date in the author and committer details.
    Returns the new commit's SHA.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/commits"
    headers = {"Authorization": f"token {token}"}
    payload: Dict[str, Any] = {
        "message": message,
        "tree": tree_sha,
        "parents": [parent_sha],
        "author": {"name": author_name, "email": author_email, "date": commit_date},
        "committer": {"name": author_name, "email": author_email, "date": commit_date},
    }
    r: requests.Response = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    data: Dict[str, Any] = r.json()
    new_sha: str = data["sha"]
    logging.info("Created new commit: %s", new_sha)
    return new_sha


def update_ref(owner: str, repo: str, branch: str, new_sha: str, token: str) -> None:
    """
    Updates the branch reference to point to the new commit SHA.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
    headers = {"Authorization": f"token {token}"}
    payload: Dict[str, Any] = {"sha": new_sha, "force": False}
    r: requests.Response = requests.patch(url, json=payload, headers=headers)
    r.raise_for_status()
    logging.info("Updated branch %s to new commit %s", branch, new_sha)


