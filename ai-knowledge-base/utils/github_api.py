"""GitHub API utility functions for retrieving repository information."""

import os
import time
from typing import Any, Dict, Optional

try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.warning(
        "loguru not installed, using standard logging. "
        "Consider installing loguru for better logging integration."
    )

# Optional import for requests; will be checked in get_repo_info
try:
    import requests
    _requests_available = True
except ImportError:
    _requests_available = False
    logger.warning(
        "The 'requests' library is not installed. "
        "Please install it with 'pip install requests' to use get_repo_info."
    )


def get_repo_info(
    owner: str,
    repo: str,
    token: Optional[str] = None,
    timeout: float = 10.0,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """Fetch basic information about a GitHub repository.

    Args:
        owner: Repository owner (username or organization).
        repo: Repository name.
        token: GitHub personal access token (optional). If not provided,
            the function will try to read from the GITHUB_TOKEN environment variable.
            Using a token increases rate limits.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on transient failures.

    Returns:
        Dictionary containing repository information with keys:
            - owner: Repository owner.
            - repo: Repository name.
            - stars: Number of stargazers.
            - forks: Number of forks.
            - description: Repository description (may be None).
            - url: GitHub URL of the repository.
            - api_url: API endpoint used.
            - fetched_at: ISO 8601 timestamp of when data was fetched.

    Raises:
        requests.exceptions.RequestException: On network errors or after max retries.
        ValueError: If the repository is not found (404) or other API errors.
    """
    if not _requests_available:
        raise ImportError(
            "The 'requests' library is required to fetch repository info. "
            "Please install it with 'pip install requests'."
        )

    # Use token from argument or environment variable
    if token is None:
        token = os.getenv("GITHUB_TOKEN")

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    logger.debug(f"Fetching repository info from {api_url}")

    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            result = {
                "owner": owner,
                "repo": repo,
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "description": data.get("description"),
                "url": data.get("html_url", f"https://github.com/{owner}/{repo}"),
                "api_url": api_url,
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            logger.info(f"Successfully fetched {owner}/{repo}: {result['stars']} stars, {result['forks']} forks")
            return result

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Repository {owner}/{repo} not found")
                raise ValueError(f"Repository {owner}/{repo} not found") from e
            elif e.response.status_code == 403:
                # Rate limit exceeded
                reset_time = e.response.headers.get("X-RateLimit-Reset")
                if reset_time:
                    wait = int(reset_time) - int(time.time())
                    if wait > 0:
                        logger.warning(f"Rate limit exceeded. Waiting {wait} seconds")
                        time.sleep(wait)
                        continue
                    else:
                        logger.info("Rate limit reset time has passed, retrying immediately")
                        continue
                logger.error("Rate limit exceeded and no reset time provided")
                raise
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"All {max_retries} attempts failed")
                raise

    # This line should never be reached, but keep it for safety
    raise RuntimeError("Unexpected exit from retry loop")


def main() -> None:
    """Example usage of get_repo_info function."""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python github_api.py <owner> <repo>")
        sys.exit(1)

    owner, repo = sys.argv[1], sys.argv[2]
    try:
        info = get_repo_info(owner, repo)
        print(f"Repository: {owner}/{repo}")
        print(f"Stars: {info['stars']}")
        print(f"Forks: {info['forks']}")
        print(f"Description: {info['description']}")
        print(f"URL: {info['url']}")
    except Exception as e:
        logger.error(f"Failed to fetch repository info: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()