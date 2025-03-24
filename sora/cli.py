from importlib.metadata import distribution
from typing import Annotated, Optional
import os

import typer

from sora.anime import Anime

app = typer.Typer()


@app.command()
def download(
    url: str,
    episodes: Annotated[
        Optional[str],
        typer.Argument(
            help="The episode to download. An expression like `1-5` can be passed to download the first 5 episodes.\
 Will be ignored if --all specefied.",
        ),
    ] = None,
    download_all: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Download all the anime. This is the default option if no episodes specified.",
        ),
    ] = None,
    quality: Annotated[
        int,
        typer.Option(
            help="1 for the lowest and 3 for the highest and 2 to download the first available of HD, SD, FHD."
        ),
    ] = 2,
    path: Annotated[
        str,
        typer.Option(
            "-p",
            "--path",
            help="The path to download episode into. The current path will be used if not passed.",
        ),
    ] = None,
) -> None:
    # url = "https://witanime.quest/episode/ao-no-hako-%d8%a7%d9%84%d8%ad%d9%84%d9%82%d8%a9-6/"
    if download_all:
        episodes = "all"
    else:
        if not episodes:
            episodes = "all"
    path = path or os.getcwd()
    anime = Anime(url, path)
    anime.download(episodes, quality)


@app.command()
def info(url: str) -> None:
    print(url)


@app.callback(invoke_without_command=True)
def cli(
    print_version: Optional[bool] = typer.Option(
        None,
        "-v",
        "--version",
        is_eager=True,
        help="Print the current version and exit",
    ),
):
    if print_version:
        project = distribution("sora")
        name = project.name
        version = project.version
        print(f"{name} {version}")
        raise typer.Exit()


def run():
    app()


if __name__ == "__main__":
    run()
