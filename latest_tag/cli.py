import typer
import requests
from os import getenv
from dotenv import load_dotenv
from loguru import logger
from typing import Optional

load_dotenv()
app = typer.Typer()


def get_headers(token: str):
    return {"Authorization": f"token {token}"}


@app.command()
def fetch(
        repo: str = typer.Option(getenv("REPO_NAME", ""), help="GitHub repo in 'owner/repo' format"),
        token: str = typer.Option(getenv("GITHUB_TOKEN", ""), help="GitHub token (env: GITHUB_TOKEN)"),
        disallow: str = typer.Option(getenv("DISALLOWED_ASSET_EXTS", ""),
                                     help="Comma-separated disallowed extensions"),
        output: str = typer.Option(getenv("LATEST_TAG_FILE", "latest_tag.txt"), help="Output file to write the tag"),

):
    """
    Fetch the latest GitHub release tag, skipping if disallowed asset types (.apk, .aab, etc.) are present.
    """
    if not repo or not token:
        logger.error("Environment variables REPO_NAME and GITHUB_TOKEN are required.")
        raise typer.Exit(code=1)

    disallowed_exts = tuple(ext.strip() for ext in disallow.split(",") if ext.strip()) if disallow else None
    logger.info(f"Fetching latest release for {repo}")
    logger.info(f"Disallowed extensions: {disallowed_exts or 'None'}")

    try:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        resp = requests.get(url, headers=get_headers(token))
        resp.raise_for_status()
        release = resp.json()

        tag = release.get("tag_name")
        assets = [a.get("name", "") for a in release.get("assets", [])]

        if disallowed_exts:
            for name in assets:
                if any(name.endswith(ext) for ext in disallowed_exts):
                    logger.warning(f"Disallowed asset found in release {tag}: {name}")
                    raise typer.Exit(code=2)

        with open(output, "w") as f:
            f.write(tag)
        logger.success(f"Release tag '{tag}' saved to {output}")

    except requests.RequestException as e:
        logger.error(f"Error fetching release: {e}")
        raise typer.Exit(code=3)
