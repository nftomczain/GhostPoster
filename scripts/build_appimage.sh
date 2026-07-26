#!/bin/bash
# Buduje przenośny GhostPoster-x86_64.AppImage.
# Uruchom w katalogu głównym repo, z aktywnym środowiskiem Python:
#
#   ./scripts/build_appimage.sh
#
# Wynik: GhostPoster-x86_64.AppImage w katalogu głównym repo — jeden plik,
# wykonywalny bezpośrednio (chmod +x), bez instalacji, na każdej
# nowszej dystrybucji Linuksa (x86_64).

set -euo pipefail
cd "$(dirname "$0")/.."

echo "Instaluję zależności (CLI + GUI + build)..."
pip install -e ".[gui,build]" --quiet

echo "Czyszczę poprzedni build..."
rm -rf build dist AppDir GhostPoster-x86_64.AppImage

echo "Buduję binarkę PyInstallerem..."
pyinstaller ghostposter.spec --noconfirm

echo "Przygotowuję AppDir..."
mkdir -p AppDir/usr/bin
cp -r dist/GhostPoster/* AppDir/usr/bin/

python3 - << 'PYEOF'
from PIL import Image
im = Image.open("docs/logo.png").convert("RGBA")
im.resize((256, 256)).save("AppDir/ghostposter.png")
PYEOF

cat > AppDir/ghostposter.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=GhostPoster
Comment=Split large PDF plans into printable sheets
Exec=GhostPoster
Icon=ghostposter
Categories=Graphics;Office;
Terminal=false
EOF

cat > AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${HERE}/usr/bin/_internal:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/GhostPoster" "$@"
EOF
chmod +x AppDir/AppRun

if [ ! -f appimagetool.AppImage ]; then
  echo "Pobieram appimagetool..."
  wget -q "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" -O appimagetool.AppImage
  chmod +x appimagetool.AppImage
fi

echo "Buduję .AppImage..."
ARCH=x86_64 ./appimagetool.AppImage AppDir GhostPoster-x86_64.AppImage

echo ""
echo "Gotowe: GhostPoster-x86_64.AppImage"
