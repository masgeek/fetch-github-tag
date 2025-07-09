# latest_tag/cli.py
import argparse
import requests
from os import getenv
from dotenv import load_dotenv
from loguru import logger

# Load .env
load_dotenv()


class Config:
    GITHUB_TOKEN = getenv('GITHUB_TOKEN')
    REPO = getenv('REPO_NAME', 'IITA-AKILIMO/akilimo-mobile')
    TAG_FILE = getenv('LATEST_TAG_FILE', 'latest_tag.txt')
    API_ROOT = "https://api.github.com"
    HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
    RAW_DISALLOWED = getenv('DISALLOWED_ASSET_EXTS', '').strip()
    DISALLOWED_ASSET_EXTS = (
        tuple(ext.strip() for ext in RAW_DISALLOWED.split(',') if ext.strip())
        if RAW_DISALLOWED else None
    )


def fetch_latest_release_tag_if_no_assets() -> str | None:
    url = f"{Config.API_ROOT}/repos/{Config.REPO}/releases/latest"
    try:
        response = requests.get(url, headers=Config.HEADERS)
        response.raise_for_status()
        release = response.json()

        tag_name = release.get('tag_name')
        assets = release.get('assets', [])
        asset_names = [asset.get('name', '') for asset in assets]

        if Config.DISALLOWED_ASSET_EXTS:
            disallowed = [
                name for name in asset_names
                if any(name.endswith(ext) for ext in Config.DISALLOWED_ASSET_EXTS)
            ]
            if disallowed:
                logger.warning(f"Release '{tag_name}' contains disallowed assets: {disallowed}")
                return None
            logger.info(f"Release '{tag_name}' passed asset check.")
        else:
            logger.info("No disallowed extensions configured. Skipping asset check.")

        return tag_name

    except requests.exceptions.RequestException as err:
        logger.error(f"Failed to fetch latest release: {err}")
        return None


def write_tag_to_file(tag: str) -> None:
    try:
        with open(Config.TAG_FILE, 'w') as f:
            f.write(tag)
        logger.info(f"Tag '{tag}' written to file: {Config.TAG_FILE}")
    except Exception as err:
        logger.error(f"Failed to write tag to file: {err}")


def cli():
    parser = argparse.ArgumentParser(description="Fetch latest GitHub release tag.")
    parser.parse_args()  # No args yet, placeholder

    logger.info(f"Repository: {Config.REPO}")
    logger.info(f"Disallowed extensions: {Config.DISALLOWED_ASSET_EXTS or 'None'}")

    tag = fetch_latest_release_tag_if_no_assets()
