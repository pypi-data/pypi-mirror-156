from genericpath import exists
from pathlib import Path, PurePath
from re import T
from typing import Optional
from pathlib import Path, PurePath
import typer
import npyscreen
app_name, version = 'saki', '1.1.1'

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
    

@app.command()
def write(path: str) -> None:
    if path == None:
        typer.echo("No path specified")
        return
    else:
        if exists(path):
            file = get_file(path=path)


            with open(file, 'r') as f:
                text = f.read()
            
            data = text
            def edit(*args):
                
                form = npyscreen.Form()

                edit = form.add(npyscreen.MultiLineEdit, name='text', value=data)

                form.edit()
                
                text = edit.value

                with open(file, 'w') as f:
                    f.write(text)
    
                return 

            npyscreen.wrapper_basic(edit)






def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{app_name} v{version}")
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


