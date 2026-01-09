import json
import re
from datetime import datetime

import requests

from ...version import Version

REPO_REGEX = re.compile(r"https://github\.com/([^/]+/[^/]+)")


def latest_version_number(repo_url: str) -> Version:
    match = REPO_REGEX.match(repo_url.removeprefix(".git"))

    if match is None:
        return Version()

    url = f"https://api.github.com/repos/{match[1]}/releases"
    response = requests.get(url)
    if response.status_code != 200:
        return Version()

    releases = json.loads(response.text)
    versions = [
        release["tag_name"].removeprefix("v")
        for release in sorted(
            releases, key=lambda x: datetime.fromisoformat(x["published_at"])
        )
    ]

    return Version(versions[-1])
