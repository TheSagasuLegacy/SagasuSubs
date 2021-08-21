import asyncio
from pathlib import Path
from typing import Optional

import click

from .auth import AuthTokenManager


@click.command()
@click.option(
    "-b", "--base", required=True, type=str, help="Base URL of Sagasu core API"
)
@click.option("-d", "--database", required=True, type=Path, help="Database file path")
@click.option(
    "-p",
    "--parallel",
    default=2,
    type=int,
    help="Number of concurrents.",
    show_default=True,
)
@click.option(
    "-t",
    "--token",
    default=None,
    type=str,
    help="HTTP JSON web token, support file path or token",
    show_default=True,
)
@click.option(
    "-b",
    "--begin",
    default=0,
    type=int,
    help="Begin index in database",
    show_default=True,
)
@click.option("-e", "--end", default=0, type=int, help="End index in database")
@click.option(
    "-s",
    "--slice",
    default=400,
    type=int,
    show_default=True,
    help="End index in database",
)
def main(
    base: str,
    database: Path,
    token: Optional[str],
    parallel: int,
    begin: int,
    end: int,
    slice: int,
):
    if token is not None:
        if (auth_file := Path(token)).is_file():
            AuthTokenManager.load_file(auth_file)
        else:
            AuthTokenManager.set_token(token)

    from SagasuSubs.api import UploadFiles

    instance = UploadFiles(database, base, slice)
    asyncio.run(
        instance.run(
            begin,
            end,
            parallel,
        )
    )


if __name__ == "__main__":
    main()
