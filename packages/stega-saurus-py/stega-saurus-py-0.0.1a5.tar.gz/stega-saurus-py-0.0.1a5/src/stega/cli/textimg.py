from pathlib import Path

from PIL import Image
import typer

from stega.image.text import encode, decode

app = typer.Typer()


def start_callback(value: int) -> int:
    if value < 0:
        raise typer.BadParameter("Must be greater than 0")
    return value


def every_px_callback(value: int) -> int:
    if value < 1:
        raise typer.BadParameter("Must be greater than 1")
    return value


def msg_callback(value: str) -> str:
    if not value:
        raise typer.BadParameter("Message must not be empty")
    return value


def key_callback(value: str) -> str:
    if not value:
        raise typer.BadParameter("Key must not be empty")
    return value


@app.callback(help='Stega-saurus text image steganography')
def text_image_callback():
    pass


@app.command(name='encode', help="Encode a message using an image output as a PNG")
def img_encode(
    in_image_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Original image path to use in encoding"
    ),
    out_image_path: Path = typer.Argument(
        ...,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
        help="Output image path to encode the message into (file extension ignored, image will be a png)"
    ),
    msg: str = typer.Argument(..., callback=msg_callback, help="Message to encode in to the image"),
):
    """
    Encode a message into a copy of an image.
    """
    typer.secho(f"stega-saurus text image steganography encode", fg=typer.colors.MAGENTA, bold=True)

    if in_image_path == out_image_path:
        typer.secho(
            f"In and out images paths are the same, this would overwrite the original file",
            fg=typer.colors.RED,
            bold=True,
            err=True
        )
        raise typer.Abort()

    typer.echo(typer.style("Encoding...", fg=typer.colors.CYAN, bold=True))

    with Image.open(in_image_path) as out_image:
        key = encode(out_image, msg)

        # Currently only supporting PNG for output file of encoding
        out_path_png = out_image_path.with_suffix('.png')
        out_image.save(out_path_png, format='png')

        typer.secho("Done encoding", fg=typer.colors.GREEN, bold=True)
        typer.secho(f"Decode key: {key}", fg=typer.colors.CYAN, bold=False)


@app.command(name='decode', help="Decode a message from an image")
def img_decode(
    in_image_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Image path with encoded msg"),
    key: str = typer.Argument(..., callback=key_callback, help="Image path with encoded msg"),
):
    """
    Decode a message from an image.
    """
    typer.secho(f"stega-saurus text image steganography decode", fg=typer.colors.MAGENTA, bold=True)
    typer.secho("Decoding...", fg=typer.colors.CYAN, bold=True)

    with Image.open(in_image_path) as in_image:
        msg = decode(in_image, key)

        typer.secho("Done decoding", fg=typer.colors.GREEN, bold=True)
        typer.secho("Encoded message:", fg=typer.colors.CYAN, bold=True)
        typer.secho(msg)


if __name__ == '__main__':
    app()
