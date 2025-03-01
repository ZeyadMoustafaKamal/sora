from sora.anime import Anime

import typer

from typing import Annotated, Optional

app = typer.Typer()

__version__ = "0.1.0"

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
            help="Download all the anime. Note that this is the default option if no episodes specified.",
        ),
    ] = None,
    quality: Annotated[
        int,
        typer.Option(
            help="1 for the lowest and 3 for the highest and 2 to download the first available of HD, SD, FHD."
        ),
    ] = 2,
) -> None:
    # url = "https://witanime.quest/episode/ao-no-hako-%d8%a7%d9%84%d8%ad%d9%84%d9%82%d8%a9-6/"
    if download_all:
        episodes = "all"
    else:
        if not episodes:
            episodes = "all"
    anime = Anime(url)
    anime.download(episodes, quality)


@app.command()
def info(url: str) -> None:
    print(url)


@app.callback(invoke_without_command=True)
def cli(
    version: Optional[bool] = typer.Option(
        None,
        "-v",
        "--version",
        is_eager=True,
        help="Print the current version and exit",
    ),
):
    if version:
        print(__version__)
        raise typer.Exit()

if __name__ == "__main__":
    app()
