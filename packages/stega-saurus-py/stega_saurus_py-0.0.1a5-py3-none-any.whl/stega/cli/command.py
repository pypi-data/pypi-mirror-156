from typing import Optional

import typer

from stega import __app_name__, __version__
from stega.cli import textimg

app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(f'{__app_name__} version: {__version__}')
        raise typer.Exit()


@app.callback(help='Stega-saurus image steganography')
def main_callback(
    version: Optional[bool] = typer.Option(None, '--version', callback=version_callback, is_eager=True)
):
    """
    Main callback method for steganography commands.
    """
    pass


app.add_typer(textimg.app, name='textimg', callback=main_callback)
