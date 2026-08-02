"""Bardzo lekki i18n dla GUI: słownik tłumaczeń PL/EN plus funkcja `t()`
do pobierania i formatowania tekstu. Żadnych zewnętrznych zależności
(gettext itp.) — to dwa języki i kilkadziesiąt krótkich napisów, słownik
w zupełności wystarczy i jest najprostszy do utrzymania.

Użycie: `t("pl", "export_button")` albo z podstawieniami:
`t("en", "status_split", count=8, paper="A3")`.
"""

from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "pl": {
        # okno / ogólne
        "window_title": "GhostPoster",
        "language_label": "Język:",
        "help_link_text": "❓ Pomoc",
        "help_action_readme": "📖 Instrukcja (README)",
        "help_action_guide": "🎬 Krótki poradnik",
        "help_action_github": "🌐 GitHub",
        "help_action_report_bug": "🐞 Zgłoś błąd",
        "help_action_about": "ℹ️ O GhostPoster",
        "quick_guide_text": (
            "Skróty klawiszowe:\n"
            "  Ctrl+O — wybierz plik PDF\n"
            "  Ctrl+E — eksportuj\n\n"
            "Strefa upuszczania pliku reaguje też na Enter/Spację po najechaniu Tabem "
            "— nie trzeba przeciągać myszką.\n\n"
            "Wskazywanie obszaru treści ręcznie:\n"
            "  przeciągnij narożniki na podglądzie\n"
            "  podwójny klik — zatwierdź zaznaczenie\n"
            "  albo wpisz współrzędne X0/Y0/X1/Y1 z klawiatury"
        ),
        "report_bug_text": (
            "Jeśli coś nie działa, uruchom GhostPoster w trybie debug:\n\n"
            "  GHOSTPOSTER_DEBUG=1 ./GhostPoster-x86_64.AppImage\n"
            "  (albo GHOSTPOSTER_DEBUG=1 ghostposter-gui przy instalacji przez pip)\n\n"
            "GhostPoster zapisze plik ghostposter_debug.txt zawierający:\n"
            "  • wersję GhostPoster\n"
            "  • wersję Pythona\n"
            "  • wersję PyMuPDF / MuPDF\n"
            "  • informacje o systemie\n"
            "  • geometrię wczytanego PDF-a\n"
            "  • przebieg eksportu\n\n"
            "Dołącz ten plik do zgłoszenia błędu na GitHubie."
        ),
        "report_bug_open_issues": "Otwórz zgłoszenia na GitHub",
        "about_text": (
            "GhostPoster {version}\n\n"
            "Dzieli duże plany PDF na mniejsze arkusze do druku w skali 1:1.\n\n"
            "Licencja: MIT\n"
            "https://github.com/nftomczain/GhostPoster"
        ),
        # strefa upuszczania
        "drop_zone_text": "Przeciągnij PDF tutaj\n(albo Enter / kliknij, żeby wybrać plik)",
        "drop_zone_chosen": "Wybrano:\n{name}",
        "drop_zone_accessible_name": "Strefa upuszczania pliku PDF",
        "drop_zone_accessible_desc": "Przeciągnij tu plik PDF, albo naciśnij Enter, żeby wybrać plik z dysku.",
        "bad_file_title": "Zły plik",
        "bad_file_body": "To nie jest plik PDF.",
        "choose_pdf_dialog": "Wybierz plik PDF",
        # podgląd
        "preview_accessible_name": "Podgląd podziału strony na arkusze",
        "preview_placeholder": "Upuść plik PDF tutaj\nlub kliknij, aby go wybrać",
        # formularz
        "paper_label": "Format arkusza:",
        "paper_accessible_name": "Format docelowego arkusza",
        "overlap_label": "Zakładka:",
        "overlap_accessible_name": "Szerokość zakładki w milimetrach",
        "page_label": "Strona źródłowa:",
        "page_accessible_name": "Numer strony źródłowego PDF",
        "crop_margin_label": "Margines wykrywania:",
        "crop_margin_accessible_name": "Margines wokół automatycznie wykrytej treści",
        "manual_crop_button": "Wskaż obszar treści...",
        "manual_crop_button_confirm": "Zatwierdź obszar",
        "manual_crop_reset_button": "Wróć do automatycznego wykrywania",
        "manual_crop_hint": "Wskazywanie obszaru treści — przeciągnij narożniki (albo kliknij dwukrotnie, żeby zatwierdzić).",
        "manual_crop_size_label": "Zaznaczony obszar\n{width} × {height} mm",
        "manual_crop_x0_label": "X0 (mm):",
        "manual_crop_y0_label": "Y0 (mm):",
        "manual_crop_x1_label": "X1 (mm):",
        "manual_crop_y1_label": "Y1 (mm):",
        "manual_crop_active_note": " · obszar treści wskazany ręcznie",
        # checkboxy
        "marks_check": "Krzyże pasowania",
        "marks_check_tooltip": "Dodaje znaczniki ułatwiające wyrównanie sklejanych arkuszy.",
        "cutlines_check": "Linie cięcia",
        "cutlines_check_tooltip": "Dodaje linie wyznaczające miejsce przycięcia zakładki.",
        "labels_check": "Numeracja + linijka",
        "labels_check_tooltip": "Dodaje etykietę arkusza (A1, B2…) i linijkę kontrolną 100 mm.",
        "maximize_check": "Auto-orientacja (--maximize)",
        "maximize_check_tooltip": "Wybiera orientację arkusza, zmniejszając liczbę stron.",
        "auto_crop_check": "Wykryj obszar treści automatycznie",
        "auto_crop_check_tooltip": "Pomija puste marginesy strony przed podziałem.",
        "print_shop_check": "Tryb Drukarnia (stempel „nie skaluj” + karta zlecenia)",
        "print_shop_check_tooltip": "Dodaje stempel „nie skaluj” w obszarze zakładki oraz kartę zlecenia druku z parametrami na początku pliku.",
        "skip_blank_check": "Pomiń puste arkusze (oszczędza papier)",
        "skip_blank_check_tooltip": "Nie generuje stron zawierających tylko puste marginesy.",
        "blank_threshold_label": "próg:",
        "blank_threshold_accessible_name": "Próg wykrywania pustych arkuszy (% atramentu)",
        # eksport
        "export_button": "Eksportuj  (Ctrl+E)",
        "export_accessible_name": "Eksportuj podzielony PDF",
        "progress_accessible_name": "Postęp eksportu",
        "save_as_dialog": "Zapisz jako",
        "no_file_title": "Brak pliku",
        "no_file_body": "Najpierw wybierz plik PDF.",
        "error_title": "Błąd podziału PDF",
        # status
        "status_ready": "Gotowe do podziału: {path}",
        "status_split": "Podział: {count} arkusz(y) formatu {paper}",
        "status_orientation_note": " (orientacja: {orientation})",
        "status_crop_note": " · Auto Crop aktywny",
        "status_processing": "Przetwarzanie...",
        "status_progress": "Zapisywanie arkusza {done}/{total}...",
        "status_saved": "Zapisano {count} arkusz(y) do {path}",
        "status_saved_skipped": " (pominięto {count} pustych)",
        "status_error": "Błąd: {message}",
        "status_page_error": "Nie udało się otworzyć PDF: {error}",
        "status_auto_crop_failed": "Auto Crop nieudany: {error}",
        "orientation_landscape": "poziomo",
        "orientation_portrait": "pionowo",
    },
    "en": {
        "window_title": "GhostPoster",
        "language_label": "Language:",
        "help_link_text": "❓ Help",
        "help_action_readme": "📖 Documentation (README)",
        "help_action_guide": "🎬 Quick guide",
        "help_action_github": "🌐 GitHub",
        "help_action_report_bug": "🐞 Report a bug",
        "help_action_about": "\u2139\ufe0f About GhostPoster",
        "quick_guide_text": (
            "Keyboard shortcuts:\n"
            "  Ctrl+O — choose a PDF file\n"
            "  Ctrl+E — export\n\n"
            "The drop zone also responds to Enter/Space once focused with Tab —\n"
            "no need to drag with the mouse.\n\n"
            "Selecting the content area manually:\n"
            "  drag the corner handles on the preview\n"
            "  double-click — confirm the selection\n"
            "  or type X0/Y0/X1/Y1 coordinates from the keyboard"
        ),
        "report_bug_text": (
            "If something isn't working, run GhostPoster in debug mode:\n\n"
            "  GHOSTPOSTER_DEBUG=1 ./GhostPoster-x86_64.AppImage\n"
            "  (or GHOSTPOSTER_DEBUG=1 ghostposter-gui if installed via pip)\n\n"
            "GhostPoster will write a ghostposter_debug.txt file containing:\n"
            "  \u2022 GhostPoster version\n"
            "  \u2022 Python version\n"
            "  \u2022 PyMuPDF / MuPDF version\n"
            "  \u2022 platform information\n"
            "  \u2022 loaded PDF geometry\n"
            "  \u2022 export progress\n\n"
            "Attach that file to your bug report on GitHub."
        ),
        "report_bug_open_issues": "Open GitHub Issues",
        "about_text": (
            "GhostPoster {version}\n\n"
            "Splits large PDF plans into smaller sheets for 1:1 scale printing.\n\n"
            "License: MIT\n"
            "https://github.com/nftomczain/GhostPoster"
        ),
        "drop_zone_text": "Drop a PDF here\n(or press Enter / click to choose a file)",
        "drop_zone_chosen": "Selected:\n{name}",
        "drop_zone_accessible_name": "PDF file drop zone",
        "drop_zone_accessible_desc": "Drop a PDF file here, or press Enter to choose one from disk.",
        "bad_file_title": "Wrong file",
        "bad_file_body": "This is not a PDF file.",
        "choose_pdf_dialog": "Choose a PDF file",
        "preview_accessible_name": "Preview of the page split into sheets",
        "preview_placeholder": "Drop a PDF file here\nor click to choose one",
        "paper_label": "Paper size:",
        "paper_accessible_name": "Target paper size",
        "overlap_label": "Overlap:",
        "overlap_accessible_name": "Overlap width in millimeters",
        "page_label": "Source page:",
        "page_accessible_name": "Source PDF page number",
        "crop_margin_label": "Detection margin:",
        "crop_margin_accessible_name": "Margin kept around the automatically detected content",
        "manual_crop_button": "Select content area...",
        "manual_crop_button_confirm": "Confirm area",
        "manual_crop_reset_button": "Back to auto-detect",
        "manual_crop_hint": "Content area selection — drag the corner handles (or double-click to confirm).",
        "manual_crop_size_label": "Selected area\n{width} \u00d7 {height} mm",
        "manual_crop_x0_label": "X0 (mm):",
        "manual_crop_y0_label": "Y0 (mm):",
        "manual_crop_x1_label": "X1 (mm):",
        "manual_crop_y1_label": "Y1 (mm):",
        "manual_crop_active_note": " \u00b7 content area set manually",
        "marks_check": "Registration marks",
        "marks_check_tooltip": "Adds marks that make it easier to align glued-together sheets.",
        "cutlines_check": "Cut lines",
        "cutlines_check_tooltip": "Adds lines marking where to trim the overlap tab.",
        "labels_check": "Labels + ruler",
        "labels_check_tooltip": "Adds a sheet label (A1, B2\u2026) and a 100 mm reference ruler.",
        "maximize_check": "Auto orientation (--maximize)",
        "maximize_check_tooltip": "Picks the sheet orientation that results in fewer pages.",
        "auto_crop_check": "Auto-detect content",
        "auto_crop_check_tooltip": "Skips blank page margins before splitting.",
        "print_shop_check": "Print Shop mode (\u201cdo not scale\u201d stamp + job sheet)",
        "print_shop_check_tooltip": "Adds a \u201cdo not scale\u201d stamp in the overlap area, plus a print job info sheet with the parameters at the start of the file.",
        "skip_blank_check": "Skip blank sheets (saves paper)",
        "skip_blank_check_tooltip": "Doesn't generate pages that contain only blank margins.",
        "blank_threshold_label": "threshold:",
        "blank_threshold_accessible_name": "Blank-sheet detection threshold (% ink)",
        "export_button": "Export  (Ctrl+E)",
        "export_accessible_name": "Export the tiled PDF",
        "progress_accessible_name": "Export progress",
        "save_as_dialog": "Save as",
        "no_file_title": "No file",
        "no_file_body": "Choose a PDF file first.",
        "error_title": "PDF split error",
        "status_ready": "Ready to split: {path}",
        "status_split": "Split: {count} sheet(s), {paper} format",
        "status_orientation_note": " (orientation: {orientation})",
        "status_crop_note": " \u00b7 Auto Crop active",
        "status_processing": "Processing...",
        "status_progress": "Writing sheet {done}/{total}...",
        "status_saved": "Saved {count} sheet(s) to {path}",
        "status_saved_skipped": " ({count} blank sheets skipped)",
        "status_error": "Error: {message}",
        "status_page_error": "Could not open the PDF: {error}",
        "status_auto_crop_failed": "Auto Crop failed: {error}",
        "orientation_landscape": "landscape",
        "orientation_portrait": "portrait",
    },
}

DEFAULT_LANG = "pl"


def t(lang: str, key: str, **kwargs: object) -> str:
    """Zwraca przetłumaczony, sformatowany tekst. Nieznany klucz/język
    nie wywala programu — zwraca klucz jako fallback, żeby brakujące
    tłumaczenie było widoczne, a nie ukryte wyjątkiem."""
    table = STRINGS.get(lang, STRINGS[DEFAULT_LANG])
    template = table.get(key) or STRINGS[DEFAULT_LANG].get(key, key)
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
