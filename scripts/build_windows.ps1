# Buduje przenośną wersję GhostPoster dla Windows.
# Uruchom w PowerShell, w katalogu głównym repo, z aktywnym środowiskiem
# Python (venv zalecany):
#
#   .\scripts\build_windows.ps1
#
# Wynik: dist\GhostPoster\GhostPoster.exe + cały folder dist\GhostPoster
# jest przenośny — spakuj go do zip i rozpakuj/uruchom na dowolnym
# Windows bez instalowania Pythona.

$ErrorActionPreference = "Stop"

Write-Host "Instaluję zależności (CLI + GUI + build)..." -ForegroundColor Cyan
pip install -e ".[gui,build]"

Write-Host "Czyszczę poprzedni build..." -ForegroundColor Cyan
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "Buduję GhostPoster.exe (PyInstaller)..." -ForegroundColor Cyan
pyinstaller ghostposter.spec --noconfirm

Write-Host ""
Write-Host "Gotowe: dist\GhostPoster\GhostPoster.exe" -ForegroundColor Green
Write-Host "Cały folder dist\GhostPoster jest przenośny (portable)."
