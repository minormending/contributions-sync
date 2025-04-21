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


