"""Punkt wejścia dla PyInstallera.

PyInstaller uruchamia wskazany plik jako skrypt najwyższego poziomu, a nie
jako moduł wewnątrz pakietu — więc importy względne w `ghostposter/gui.py`
(`from .blank import ...` itd.) by się wywaliły, gdyby to jego wskazać
bezpośrednio jako punkt wejścia. Ten plik jest cienką nakładką importującą
`ghostposter` jako normalny, zainstalowany pakiet, dzięki czemu importy
względne w środku działają tak samo jak przy `ghostposter-gui`.
"""
import os
import sys
import fitz
import platform
from pathlib import Path
from datetime import datetime
from ghostposter import __version__

if os.getenv("GHOSTPOSTER_DEBUG") == "1":
    log = Path.cwd() / "ghostposter_debug.txt"

    with open(log, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("GhostPoster diagnostics\n")
        f.write("=" * 60 + "\n")
        f.write(f"GhostPoster: {__version__}\n")
        f.write(f"Python    : {sys.version}\n")
        f.write(f"Executable: {sys.executable}\n")
        f.write(f"fitz      : {fitz.__file__}\n")
        f.write(f"PyMuPDF   : {fitz.VersionBind}\n")
        f.write(f"MuPDF     : {fitz.VersionFitz}\n")
        f.write(f"Frozen    : {getattr(sys, 'frozen', False)}\n")
        f.write(f"MEIPASS   : {getattr(sys, '_MEIPASS', None)}\n")
        f.write(f"Platform  : {platform.platform()}\n")
        f.write(f"Machine   : {platform.machine()}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Timestamp : {datetime.now().isoformat()}\n")
        f.write("Status    : startup OK\n")
        
from ghostposter.gui import main

if __name__ == "__main__":
    main()
