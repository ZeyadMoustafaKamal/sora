from anime import Anime

import typer

from typing import Annotated

app = typer.Typer()


@app.command()
def download(
    url: str,
    episodes: Annotated[
        str,
        typer.Option(
            "-e",
            "--episodes",
            help="The episodes line. You should pass the number of the episode to download \
or you can pass something like 1-5 to download from the episode number 1 to the number 5. Will be ignored if --all is passed",
        ),
    ] = None,
    download_all: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Download all episodes of the anime. Note that this is the default option if not --line",
        ),
    ] = None,
    quality: Annotated [
    int, typer.Option(help="The quality of the episodes. You can choose 1 for the lowest possible or 2 for the\
    HD quality of exists or SD if no HD quality or FHD if not HD or SD available or 3 for the highest possible.")
    ] = 2
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


if __name__ == "__main__":
    app()
