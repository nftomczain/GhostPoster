import os
import sys
import fitz
import platform
from pathlib import Path
from datetime import datetime

try:
    from ghostposter import __version__
except Exception:
    __version__ = "unknown"

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
    _LOG.write(f"Frozen    : {getattr(sys,'frozen',False)}\n")
    _LOG.write(f"MEIPASS   : {getattr(sys,'_MEIPASS',None)}\n")
    _LOG.write(f"Platform  : {platform.platform()}\n")
    _LOG.write(f"Machine   : {platform.machine()}\n")
    _LOG.write(f"Timestamp : {datetime.now().isoformat()}\n")
    _LOG.write("Status    : startup OK\n")
    _LOG.write("=" * 60 + "\n\n")
    _LOG.flush()


def debug(msg=""):
    if _LOG:
        _LOG.write(str(msg) + "\n")
        _LOG.flush()


def pdf_info(path, doc):
    if not _LOG:
        return

    page = doc[0]

    debug("INPUT PDF")
    debug("-" * 60)
    debug(f"File      : {path}")
    debug(f"Pages     : {doc.page_count}")
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

def export_info(input_path, output_path, tiles):
    if not _LOG:
        return

    debug("EXPORT")
    debug("-" * 60)
    debug(f"Input     : {input_path}")
    debug(f"Output    : {output_path}")
    debug(f"Tiles     : {len(tiles)}")
    debug("")