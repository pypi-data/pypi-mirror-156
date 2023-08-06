from genericpath import exists
from pathlib import Path, PurePath
from typing import Optional
from pathlib import Path, PurePath
import typer


__app_name__ = "saki"
__version__ = "1.0.0"

app = typer.Typer()

SIZE = 64*1024




def get_file(path: str) -> PurePath:
    file = Path(path)

    return file

@app.command()
def read(path: str) -> None:
    if path == None:
        typer.echo("No path specified")
        return
    else:
        if exists(path):
            file = get_file(path=path)

            with open(file, 'r') as f:
                chunk = f.read(SIZE)

                while len(chunk) > 0:
                    typer.echo(chunk)
                    chunk = f.read(SIZE)
    

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
