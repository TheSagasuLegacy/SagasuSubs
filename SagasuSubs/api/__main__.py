import asyncio
from pathlib import Path

import click


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
def main(base: str, database: Path, parallel: int, begin: int, end: int, slice: int):
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
