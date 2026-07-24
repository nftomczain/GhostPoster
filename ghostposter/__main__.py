"""Pozwala uruchomić GhostPoster jako `python -m ghostposter`.

Właściwa logika CLI zostaje w `cli.py` — ten plik jest cienką nakładką,
żeby nazwa modułu (`cli`) w kodzie pozostała czytelna dla kogoś, kto
przegląda pakiet, a jednocześnie `-m ghostposter` działało od razu,
bez instalacji.
"""

from .cli import main

if __name__ == "__main__":
    main()
