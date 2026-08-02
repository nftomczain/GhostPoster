<p align="center">
  <a href="README.md">English</a> · <b>Polski</b>
</p>

<p align="center">
  <img src="docs/logo.png" alt="GhostPoster logo" width="180">
</p>

<h1 align="center">GhostPoster</h1>
<p align="center"><b>Professional PDF Tiling & Poster Generator</b></p>
<p align="center">
  Dziel duże plany PDF na mniejsze arkusze (A4, A3, A2…) i drukuj je na zwykłej
  drukarce w skali 1:1, ze wspólną zakładką do sklejania.
</p>

<h2 align="center">PDF in. Plan out.</h2>


<p align="center">
  <a href="https://github.com/nftomczain/GhostPoster/actions"><img alt="CI" src="https://img.shields.io/badge/CI-GitHub%20Actions-blue"></a>
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="version" src="https://img.shields.io/github/v/release/nftomczain/GhostPoster?display_name=tag">
 <img alt="Platform" src="https://img.shields.io/badge/Platform-Linux AppImage-green">
</p>

---

## Zrzuty ekranu

| Okno programu (GUI) | Wygenerowany PDF |
|---|---|
| ![GUI](docs/screenshots/gui_window.png) | ![Wygenerowany PDF](docs/screenshots/generated_pdf.png) |

Po lewej: podgląd na żywo z nałożoną siatką (tu z włączonym automatycznym
wykrywaniem treści — program sam znalazł realny obszar rysunku i pominął
puste marginesy). Po prawej: jeden z wygenerowanych arkuszy — widać krzyże
pasowania (niebieskie), linie cięcia (czerwone przerywane), numerację
arkusza, linijkę kontrolną 100 mm i kwadrat kalibracyjny 50×50 mm.

---

## Funkcje

| Funkcja | Opis |
|---|---|
| **Podział na arkusze** | ISO A0–A6, Letter/Legal/Tabloid, ANSI A–E, ARCH A–E1 — zakładka 0–50 mm, skala zawsze 100% (bez przeskalowania) |
| **Auto-orientacja (`--maximize`)** | Sam dobiera pionowo/poziomo dla wybranego formatu, żeby zminimalizować liczbę kartek |
| **Automatyczne wykrywanie treści** | Wykrywa rzeczywisty obszar rysunku i pomija puste marginesy strony przed podziałem |
| **Wskazanie obszaru treści ręcznie** | Gdy automatyczne wykrywanie nie trafi — przeciągnij narożniki na podglądzie (jak w CAD) albo wpisz współrzędne, `--crop-rect` w CLI |
| **Wykrywanie pustych arkuszy** | Ostrzega albo automatycznie pomija arkusze, które wyszłyby praktycznie puste — oszczędza papier |
| **Znaczniki kontrolne** | Krzyże pasowania, linie cięcia, numeracja arkusza (A1, B2…), linijka 100 mm, kwadrat kalibracyjny 50×50 mm |
| **Tryb Drukarnia** | Stempel „nie skaluj” w obszarze zakładki + karta zlecenia druku z parametrami na początku pliku |
| **Podgląd na żywo (GUI)** | Siatka podziału aktualizuje się natychmiast po zmianie formatu, zakładki czy opcji |
| **Metadane PDF** | Title/Creator/Producer ustawione w każdym wygenerowanym pliku |
| **Polskie znaki** | Poprawne renderowanie ą ć ę ł ń ó ś ź ż (dołączona czcionka DejaVu Sans) |
| **Wieloplatformowość** | Linux, Windows, macOS — CI sprawdza wszystkie trzy na każdym pushu |

## Instalacja

```bash
git clone https://github.com/nftomczain/GhostPoster.git
cd GhostPoster
pip install -e .          # samo CLI
pip install -e ".[gui]"   # CLI + GUI (PySide6)
```

## Szybki start

```bash
ghostposter plan.pdf --paper A3 --overlap 15 --maximize --auto-crop --output plan_A3.pdf
```

To wystarczy na start: program sam dobierze orientację arkusza, przytnie
puste marginesy i zapisze gotowe do druku arkusze A3 z 15 mm zakładką.

## GUI

```bash
ghostposter-gui
```

Przeciągnij PDF (albo wybierz plik przyciskiem/Enterem), ustaw format
i zakładkę, zaznacz potrzebne opcje, eksportuj. Podgląd z nałożoną siatką
aktualizuje się na żywo — również po włączeniu automatycznego wykrywania
treści, zmianie jego marginesu czy pomijania pustych arkuszy — a eksport
pokazuje realny pasek postępu.

Jeśli automatyczne wykrywanie źle sobie radzi z nietypowym PDF-em (np.
cienka ramka sięgająca krawędzi strony), przycisk „Wskaż obszar treści...”
pozwala zaznaczyć go ręcznie: przeciągasz narożniki prosto na podglądzie
(jak w CAD-zie — dwuklik zatwierdza zaznaczenie), albo wpisujesz dokładne
współrzędne X0/Y0/X1/Y1 w milimetrach — w pełni dostępne z klawiatury.
Startowy prostokąt automatycznie dopasowuje się do wykrytej treści (jeśli
to możliwe), a nie do całej strony, a rozmiar zaznaczenia jest widoczny na
żywo podczas przeciągania. „Wróć do automatycznego wykrywania” cofa ręczne
zaznaczenie.

Interfejs jest dwujęzyczny (PL/EN, przełącznik w prawym górnym rogu okna).
Ostatnio użyty język, format, zakładka, margines wykrywania treści
i wszystkie checkboxy (`--maximize`, `--auto-crop`, pomijanie pustych
arkuszy, tryb Drukarnia) są zapamiętywane między uruchomieniami.

Przy starcie pojawia się krótki splash screen, a menu „❓ Pomoc” w prawym
górnym rogu prowadzi do instrukcji, krótkiego poradnika, GitHuba,
zgłaszania błędów (razem z prawdziwym trybem diagnostycznym
`GHOSTPOSTER_DEBUG=1`) i okna „O GhostPoster”.

Zaprojektowane pod obsługę jedną ręką — każda akcja dostępna też
z klawiatury (`Ctrl+O` otwiera plik, `Ctrl+E` eksportuje) — i pod czytniki
ekranu (opisane `accessibleName` na każdej kontrolce).

## CLI

```bash
ghostposter plan.pdf --paper A3 --overlap 15 --marks --cutlines --labels --output plan_A3.pdf
```

| Opcja | Opis | Domyślnie |
|---|---|---|
| `--paper` | Format arkusza docelowego: A0–A6, Letter, Legal, Tabloid, ANSI-A–E, ARCH-A–E1 | `A4` |
| `--overlap` | Szerokość zakładki w mm (0–50) | `10` |
| `--page` | Numer strony źródłowego PDF (od 0) | `0` |
| `--output` | Ścieżka pliku wynikowego | `<nazwa>_tiled.pdf` |
| `--maximize` | Auto-orientacja arkusza — mniej kartek, skala zawsze 100% | wyłączone |
| `--auto-crop` | Przytnij do rzeczywistego obszaru rysunku przed podziałem | wyłączone |
| `--crop-margin` | Margines (mm) wokół wykrytej treści przy `--auto-crop`: 0/2/5/10/20 | `5` |
| `--skip-blank` | Pomiń automatycznie wykryte puste arkusze (bez pytania) | wyłączone |
| `--keep-blank` | Zachowaj pełną siatkę, nawet jeśli część arkuszy wyjdzie pusta | wyłączone |
| `--blank-threshold` | Próg wykrywania pustych arkuszy w % atramentu — podnieś, jeśli cienka linia ramki arkusza sprawia, że prawie puste kafelki nie są rozpoznawane jako puste | `0.5` |
| `--crop-rect` | Ręcznie zdefiniowany obszar treści `'x0,y0,x1,y1'` w mm — pomija automatyczne wykrywanie, przydatne gdy ono sobie nie radzi | brak (auto) |
| `--marks` | Krzyże pasowania na wspólnych zakładkach | wyłączone |
| `--cutlines` | Linie cięcia na wspólnych zakładkach | wyłączone |
| `--labels` | Numeracja arkusza + linijka 100 mm + kwadrat 50×50 mm | wyłączone |
| `--print-shop` | Tryb Drukarnia: stempel „nie skaluj” + karta zlecenia druku | wyłączone |

Bez żadnej flagi dotyczącej pustych arkuszy: jeśli program wykryje puste
arkusze, w terminalu interaktywnym zapyta, czy je pominąć; w skrypcie
(np. w CI) po prostu je zachowa i podpowie użycie `--skip-blank`.

Uruchomienie bez instalacji: `python -m ghostposter ...`

## Przykłady

W `examples/` są syntetyczne pliki testowe (generowane przez
`scripts/generate_examples.py`) pokrywające różne przypadki:

| Plik | Przypadek |
|---|---|
| `plan_A0_poster.pdf` | Pojedyncza strona w formacie A0 |
| `plan_large_margins.pdf` | Treść tylko w środkowym bloku — dobry test dla `--auto-crop` |
| `plan_multipage.pdf` | 3 strony o różnych rozmiarach — test `--page` |
| `plan_wide_strip.pdf` | Bardzo szeroki, niski plan — dobry test dla `--maximize` |

```bash
ghostposter examples/plan_large_margins.pdf --paper A4 --auto-crop --output out.pdf
```

## Przenośna wersja dla systemu Linux (AppImage)

Jeden plik, bez instalacji, bez `pip install`:

1. [GitHub Actions](https://github.com/nftomczain/GhostPoster/actions) →
   najnowszy udany przebieg **CI** → artefakt **GhostPoster-x86_64-AppImage**.
2. `chmod +x GhostPoster-x86_64.AppImage`
3. `./GhostPoster-x86_64.AppImage`

Zbudować samodzielnie:

```bash
./scripts/build_appimage.sh
```

## Wsparcie dla Windows

### Chcesz pomóc?

Szukam osób, które mogłyby pomóc w budowaniu, testowaniu i dopracowaniu natywnej wersji GhostPostera dla systemu Windows.

Szczególnie przyda się pomoc w:

- budowaniu projektu na Windows 10/11 przy użyciu PyInstallera,
- testowaniu wygenerowanego programu,
- zgłaszaniu problemów specyficznych dla Windows,
- usprawnianiu procesu tworzenia pakietów,
- automatyzacji wydań Windows w GitHub Actions.

Repozytorium: https://github.com/nftomczain/GhostPoster

Każda pomoc będzie bardzo mile widziana!

Jeśli chcesz zbudować GhostPostera samodzielnie w systemie Windows:

```powershell
.\scripts\build_windows.ps1
```

Gotowa przenośna wersja zostanie utworzona w katalogu `dist\GhostPoster\`. Cały folder można spakować i przekazać innej osobie — instalacja nie jest wymagana.

## CI

GitHub Actions (`.github/workflows/ci.yml`) uruchamia na każdym pushu i PR
do `main`: `ruff check`, `black --check`, `pytest` (macierz Linux/Windows/macOS
× Python 3.10–3.12), budowę paczki (`python -m build`), przenośny
`GhostPoster.exe` na Windows i przenośny `GhostPoster-x86_64.AppImage` na
Linuksie (oba jako PyInstaller).

## Historia wydań

Pełna historia zmian znajduje się w GitHub Releases.

### v1.0.0

- Pierwsze stabilne wydanie
- Automatyczne wykrywanie obszaru treści
- Ręczne wskazywanie obszaru treści
- Graficzny interfejs użytkownika (GUI)
- Interfejs wiersza poleceń (CLI)
- Przenośna wersja AppImage

## Pomysły na kolejne wersje:

- paczka macOS (`.app`/DMG)
- Flatpak (obok istniejącego AppImage)
- konfigurowalny styl numeracji arkuszy (litera=wiersz zamiast litera=kolumna)

### Wsparcie dla macOS

GhostPoster jest projektem wieloplatformowym, jednak obecnie nie mam możliwości budowania i testowania natywnych wydań dla macOS.
## Wsparcie

GhostPoster jest darmowym i otwartym oprogramowaniem.

Jeśli projekt okazał się dla Ciebie przydatny, możesz wesprzeć jego dalszy rozwój na Liberapay.

[![Liberapay](https://img.shields.io/badge/Liberapay-Wesprzyj-F6C915?logo=liberapay&logoColor=black)](https://liberapay.com/nftomczain/)


Jeśli masz komputer Mac i chciałbyś pomóc w testowaniu lub przygotowaniu wersji dla macOS, zapraszam do współpracy.

## Licencja

MIT — zobacz [LICENSE](LICENSE).
