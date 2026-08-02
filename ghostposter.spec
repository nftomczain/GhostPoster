# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec dla przenośnego GhostPoster.exe (Windows, tryb GUI).

Budowanie (na Windows, w środowisku z zainstalowanym `ghostposter[gui]`
i `pyinstaller`):

    pyinstaller ghostposter.spec

Wynik: dist/GhostPoster/GhostPoster.exe (tryb --onedir — szybszy start
i łatwiejszy debugging niż --onefile; cały folder dist/GhostPoster jest
przenośny — spakuj go do zip i wyślij komuś, nie trzeba instalatora).
"""

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Czcionki DejaVu (polskie znaki w generowanych PDF-ach) muszą pojechać
# jako dane, bo są wczytywane w runtime przez ścieżkę względem pakietu.
font_datas = collect_data_files("ghostposter", includes=["fonts/*.ttf", "fonts/LICENSE.txt"])
asset_datas = collect_data_files("ghostposter", includes=["assets/*.png"])

a = Analysis(
    ["pyinstaller_entry.py"],
    pathex=[],
    binaries=[],
    datas=font_datas + asset_datas,
    hiddenimports=["fitz", "PIL", "PIL._tkinter_finder"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy.testing"],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GhostPoster",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # okno GUI, bez konsoli w tle
    icon="docs/logo.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="GhostPoster",
)
