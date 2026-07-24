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
        "preview_placeholder": "Brak podglądu\n(wybierz plik PDF)",
        # formularz
        "paper_label": "Format arkusza:",
        "paper_accessible_name": "Format docelowego arkusza",
        "overlap_label": "Zakładka:",
        "overlap_accessible_name": "Szerokość zakładki w milimetrach",
        "page_label": "Strona źródłowa:",
        "page_accessible_name": "Numer strony źródłowego PDF",
        "crop_margin_label": "Margines Auto Crop:",
        "crop_margin_accessible_name": "Margines wokół wykrytej treści przy Auto Crop",
        # checkboxy
        "marks_check": "Krzyże pasowania",
        "cutlines_check": "Linie cięcia",
        "labels_check": "Numeracja + linijka",
        "maximize_check": "Auto-orientacja (--maximize)",
        "auto_crop_check": "Auto Crop (przytnij do treści)",
        "print_shop_check": "Tryb Drukarnia (stempel „nie skaluj” + karta zlecenia)",
        "skip_blank_check": "Pomiń puste arkusze (oszczędza papier)",
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
        "drop_zone_text": "Drop a PDF here\n(or press Enter / click to choose a file)",
        "drop_zone_chosen": "Selected:\n{name}",
        "drop_zone_accessible_name": "PDF file drop zone",
        "drop_zone_accessible_desc": "Drop a PDF file here, or press Enter to choose one from disk.",
        "bad_file_title": "Wrong file",
        "bad_file_body": "This is not a PDF file.",
        "choose_pdf_dialog": "Choose a PDF file",
        "preview_accessible_name": "Preview of the page split into sheets",
        "preview_placeholder": "No preview\n(choose a PDF file)",
        "paper_label": "Paper size:",
        "paper_accessible_name": "Target paper size",
        "overlap_label": "Overlap:",
        "overlap_accessible_name": "Overlap width in millimeters",
        "page_label": "Source page:",
        "page_accessible_name": "Source PDF page number",
        "crop_margin_label": "Auto Crop margin:",
        "crop_margin_accessible_name": "Margin kept around detected content for Auto Crop",
        "marks_check": "Registration marks",
        "cutlines_check": "Cut lines",
        "labels_check": "Labels + ruler",
        "maximize_check": "Auto orientation (--maximize)",
        "auto_crop_check": "Auto Crop (trim to content)",
        "print_shop_check": "Print Shop mode (\u201cdo not scale\u201d stamp + job sheet)",
        "skip_blank_check": "Skip blank sheets (saves paper)",
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
