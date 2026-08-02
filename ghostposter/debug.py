"""Tryb debug: aktywowany zmienną środowiskową `GHOSTPOSTER_DEBUG=1`.

Zapisuje diagnostykę do `ghostposter_debug.txt` w bieżącym katalogu —
wersję GhostPoster, Pythona (łącznie ze ścieżką do interpretera), wersję
PyMuPDF/MuPDF, czy program działa jako spakowana binarka PyInstallera
(`Frozen`/`MEIPASS` — przydatne przy diagnozowaniu problemów specyficznych
dla AppImage/.exe, których nie da się odtworzyć z normalnej instalacji
przez pip), informacje o platformie, geometrię wczytywanego PDF-a
(rotacja, mediabox, cropbox, macierze transformacji) i przebieg eksportu.
Przydatne przy zgłaszaniu błędów, żeby nie trzeba było tego wszystkiego
opisywać ręcznie.

Użycie:

    GHOSTPOSTER_DEBUG=1 ghostposter-gui
    GHOSTPOSTER_DEBUG=1 ./GhostPoster-x86_64.AppImage

Plik jest otwierany raz, przy pierwszym imporcie tego modułu (czyli przy
starcie programu) — każde uruchomienie dostaje świeży log, nie dopisuje
do poprzedniego. Gdy zmienna środowiskowa nie jest ustawiona, wszystkie
funkcje w tym module są no-op — zero kosztu w normalnym użytkowaniu.
"""

from __future__ import annotations

import os
import platform
import sys
from datetime import datetime
from pathlib import Path

import fitz

from . import __version__

DEBUG = os.getenv("GHOSTPOSTER_DEBUG") == "1"

_LOG = None

if DEBUG:
    _LOG = open(Path.cwd() / "ghostposter_debug.txt", "w", encoding="utf-8")

    _LOG.write("=" * 60 + "\n")
    _LOG.write("GhostPoster diagnostics\n")
    _LOG.write("=" * 60 + "\n")
    _LOG.write(f"GhostPoster: {__version__}\n")
    _LOG.write(f"Python    : {sys.version}\n")
    _LOG.write(f"Executable: {sys.executable}\n")
    _LOG.write(f"fitz      : {fitz.__file__}\n")
    _LOG.write(f"PyMuPDF   : {fitz.VersionBind}\n")
    _LOG.write(f"MuPDF     : {fitz.VersionFitz}\n")
    _LOG.write(f"Frozen    : {getattr(sys, 'frozen', False)}\n")
    _LOG.write(f"MEIPASS   : {getattr(sys, '_MEIPASS', None)}\n")
    _LOG.write(f"Platform  : {platform.platform()}\n")
    _LOG.write(f"Machine   : {platform.machine()}\n")
    _LOG.write(f"Timestamp : {datetime.now().isoformat()}\n")
    _LOG.write("Status    : startup OK\n")
    _LOG.write("=" * 60 + "\n\n")
    _LOG.flush()


def debug(msg: object = "") -> None:
    if _LOG:
        _LOG.write(str(msg) + "\n")
        _LOG.flush()


def pdf_info(path: Path, doc: fitz.Document, page_number: int = 0) -> None:
    """Loguje geometrię wybranej strony `doc` (domyślnie strony 0).

    `page_number` odpowiada temu, którą stronę faktycznie dzieli GhostPoster
    (patrz `write_tiled_pdf`) — dla wielostronicowych PDF-ów samo zalogowanie
    strony 0 byłoby mylące, gdyby użytkownik dzielił np. stronę 2.
    """
    if not _LOG:
        return

    page = doc[page_number]

    debug("INPUT PDF")
    debug("-" * 60)
    debug(f"File      : {path}")
    debug(f"Pages     : {doc.page_count}")
    debug(f"Page used : {page_number}")
    debug(f"Rotation  : {page.rotation}")
    debug(f"MediaBox  : {page.mediabox}")
    debug(f"CropBox   : {page.cropbox}")
    debug(f"Rect      : {page.rect}")
    debug(f"Bound     : {page.bound()}")
    debug(f"Matrix    : {page.transformation_matrix}")
    debug(f"Derotation: {page.derotation_matrix}")
    debug(f"CropBox Pos : {page.cropbox_position}")
    debug(f"RotationMat : {page.rotation_matrix}")
    debug("")


def export_info(input_path: Path, output_path: Path, tiles: list) -> None:
    if not _LOG:
        return

    debug("EXPORT")
    debug("-" * 60)
    debug(f"Input     : {input_path}")
    debug(f"Output    : {output_path}")
    debug(f"Tiles     : {len(tiles)}")
    debug("")
