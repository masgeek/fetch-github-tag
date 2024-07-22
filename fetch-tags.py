from os import getenv

import requests
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Retrieve necessary environment variables
gitToken = getenv('GITHUB_TOKEN')
repo = getenv('REPO_NAME', 'IITA-AKILIMO/akilimo-mobile')
tagFile = getenv('LATEST_TAG_FILE', 'latest_tag.txt')
baseBranch = getenv('BASE_BRANCH', 'main')

# Define the GitHub API root URL
rootUrl = "https://api.github.com"

# Construct the URL for pull requests
pulls_url = f"{rootUrl}/repos/{repo}/pulls?base={baseBranch}&state=open"
headers = {'Authorization': f'token {gitToken}'}

logger.info(f"Fetching latest tags from {repo}")


@logger.catch
def get_pull_request():
    """Fetch open pull requests for the repository."""
    try:
        response = requests.get(pulls_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logger.error(f'Error occurred while fetching pull requests: {err}')
        return None


@logger.catch
def latest_tag():
    """Fetch the latest release tag for the repository."""
    try:
        releases_url = f"{rootUrl}/repos/{repo}/releases/latest"
        response = requests.get(releases_url, headers=headers)
        response.raise_for_status()
        tag_resp = response.json()
        return tag_resp['tag_name']

    except requests.exceptions.RequestException as err:
        logger.error(f'Error occurred while fetching the latest tag: {err}')
        return None


@logger.catch
def get_tag_from_pull_request():
    """Attempt to get the tag from the latest pull request title."""
    try:
        pull_requests = get_pull_request()
        if pull_requests:
            logger.info(f'Pull request title: {pull_requests[0]["title"]}')

            tag_arr = pull_requests[0]['title'].split()
            return tag_arr[len(tag_arr) - 1]
        else:
            logger.warning('No pull requests fetched, fetching from tags')
            return None
    except (IndexError, KeyError, TypeError) as err:
        logger.error(f'Error occurred while getting tag from pull requests: {err}')
        return None


@logger.catch
def write_tag_to_file(release_tag):
    """Write the tag to the specified file."""
    try:
        with open(tagFile, "w") as file:
            file.write(release_tag)
        logger.info(f'Tag created: {release_tag}')
    except Exception as err:
        logger.error(f'An error occurred while writing the tag to the file: {err}')


# Main execution block
if __name__ == "__main__":

    prs = get_pull_request()
    for pr in prs:
        logger.info(pr.get('title'))
    exit(6000)
    # Fetch tag from pull request or latest release
    tag = get_tag_from_pull_request()

    if tag is None:
        tag = latest_tag()

    logger.info(f'Tag: {tag}')

    if tag:
        write_tag_to_file(tag)
    else:
        logger.error('Failed to fetch tag. Exiting.')
