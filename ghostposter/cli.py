"""Interfejs wiersza poleceń GhostPoster.

Przykład:

    ghostposter plan.pdf --paper A3 --overlap 15 --output plan_A3.pdf
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress

from .blank import find_blank_tiles
from .config import TileJobConfig
from .crop import detect_content_bbox
from .geometry import compute_best_grid, compute_grid, translate_tiles
from .paper import UnknownPaperSizeError, available_sizes, get_paper_size_pt
from .tiler import PageNumberOutOfRangeError, get_page_size_pt
from .utils import mm_to_pt, pt_to_mm
from .writer import write_tiled_pdf

console = Console()


@click.command()
@click.argument("input_pdf", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--paper",
    default="A4",
    show_default=True,
    help=f"Format docelowego arkusza. Dostępne: {', '.join(available_sizes())}",
)
@click.option(
    "--overlap",
    "overlap_mm",
    default=10.0,
    show_default=True,
    type=click.FloatRange(0, 50),
    help="Szerokość zakładki (nachodzenia arkuszy) w mm, 0–50.",
)
@click.option(
    "--page",
    "page_number",
    default=0,
    show_default=True,
    help="Numer strony źródłowego PDF do podziału (liczone od 0).",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Ścieżka pliku wynikowego (domyślnie <nazwa>_tiled.pdf).",
)
@click.option("--marks", is_flag=True, help="Krzyże pasowania na wspólnych zakładkach.")
@click.option("--cutlines", is_flag=True, help="Linie cięcia na wspólnych zakładkach.")
@click.option(
    "--labels",
    is_flag=True,
    help="Numeracja arkusza (A1, B2...) + linijka 100 mm + kwadrat kalibracyjny 50x50 mm.",
)
@click.option(
    "--maximize",
    "maximize",
    is_flag=True,
    help="Sam dobiera orientację arkusza (pionowo/poziomo), żeby zminimalizować liczbę kartek (skala zawsze 100%).",
)
@click.option(
    "--print-shop",
    "print_shop",
    is_flag=True,
    help="Tryb Drukarnia: stempel „nie skaluj” na każdym arkuszu + karta zlecenia druku na początku pliku.",
)
@click.option(
    "--skip-blank",
    "skip_blank",
    is_flag=True,
    help="Pomiń automatycznie wykryte puste arkusze (bez pytania) — oszczędza papier.",
)
@click.option(
    "--keep-blank",
    "keep_blank",
    is_flag=True,
    help="Zachowaj pełną siatkę arkuszy, nawet jeśli niektóre wyjdą puste (bez pytania, bez sprawdzania).",
)
@click.option(
    "--auto-crop",
    "auto_crop",
    is_flag=True,
    help="Przytnij do rzeczywistego obszaru rysunku przed podziałem — mniejsza, sensowniejsza siatka zamiast pustych marginesów.",
)
@click.option(
    "--crop-margin",
    "crop_margin_mm",
    type=click.Choice(["0", "2", "5", "10", "20"]),
    default="5",
    show_default=True,
    help="Margines (mm) zostawiony wokół wykrytej treści przy --auto-crop — przydatne, gdy cienka linia dochodzi do samej krawędzi.",
)
def main(
    input_pdf: Path,
    paper: str,
    overlap_mm: float,
    page_number: int,
    output_path: Path | None,
    marks: bool,
    cutlines: bool,
    labels: bool,
    maximize: bool,
    print_shop: bool,
    skip_blank: bool,
    keep_blank: bool,
    auto_crop: bool,
    crop_margin_mm: str,
) -> None:
    """Dzieli duży PDF (INPUT_PDF) na mniejsze arkusze gotowe do druku i sklejenia."""
    if output_path is None:
        output_path = input_pdf.with_name(f"{input_pdf.stem}_tiled.pdf")

    config = TileJobConfig(
        input_path=input_pdf,
        output_path=output_path,
        paper=paper,
        overlap_mm=overlap_mm,
        page_number=page_number,
        marks=marks,
        cutlines=cutlines,
        labels=labels,
        maximize=maximize,
        print_shop=print_shop,
        skip_blank=skip_blank,
        keep_blank=keep_blank,
        auto_crop=auto_crop,
        crop_margin_mm=float(crop_margin_mm),
    )

    try:
        paper_width_pt, paper_height_pt = get_paper_size_pt(config.paper)
    except UnknownPaperSizeError as exc:
        raise click.ClickException(str(exc)) from exc

    try:
        page_width_pt, page_height_pt = get_page_size_pt(config.input_path, config.page_number)
    except PageNumberOutOfRangeError as exc:
        raise click.ClickException(str(exc)) from exc

    overlap_pt = mm_to_pt(config.overlap_mm)

    effective_width_pt, effective_height_pt = page_width_pt, page_height_pt
    offset_x, offset_y = 0.0, 0.0
    if config.auto_crop:
        bbox = detect_content_bbox(
            config.input_path, config.page_number, padding_mm=config.crop_margin_mm
        )
        effective_width_pt, effective_height_pt = bbox.width, bbox.height
        offset_x, offset_y = bbox.x0, bbox.y0
        console.print(
            f"--auto-crop: {pt_to_mm(page_width_pt):.0f}x{pt_to_mm(page_height_pt):.0f} mm → "
            f"{pt_to_mm(effective_width_pt):.0f}x{pt_to_mm(effective_height_pt):.0f} mm "
            "(pominięto puste marginesy strony)."
        )

    try:
        if config.maximize:
            result = compute_best_grid(
                effective_width_pt, effective_height_pt, paper_width_pt, paper_height_pt, overlap_pt
            )
            tiles = result.tiles
            paper_width_pt, paper_height_pt = result.paper_width_pt, result.paper_height_pt
            console.print(
                f"--maximize: wybrano orientację {result.orientation} "
                f"formatu {config.paper} → {len(tiles)} arkusz(y) (zamiast więcej w drugiej orientacji)."
            )
        else:
            tiles = compute_grid(
                effective_width_pt, effective_height_pt, paper_width_pt, paper_height_pt, overlap_pt
            )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if offset_x or offset_y:
        tiles = translate_tiles(tiles, offset_x, offset_y)

    console.print(
        f"Strona {config.page_number}: podział na {len(tiles)} arkusz(y) formatu {config.paper}."
    )

    skip_labels: set[str] = set()
    if not config.keep_blank:
        blanks = find_blank_tiles(config.input_path, tiles, config.page_number)
        if blanks:
            blank_labels = [t.label for t in blanks]
            if config.skip_blank:
                skip_labels = set(blank_labels)
                console.print(
                    f"[yellow]Pomijam {len(blanks)} pusty(ch) arkusz(y):[/yellow] {', '.join(blank_labels)}"
                )
            elif sys.stdin.isatty():
                if click.confirm(
                    f"Wykryto {len(blanks)} praktycznie pusty(ch) arkusz(y) "
                    f"({', '.join(blank_labels)}). Pominąć je?",
                    default=False,
                ):
                    skip_labels = set(blank_labels)
            else:
                console.print(
                    f"[yellow]Uwaga:[/yellow] {len(blanks)} arkusz(y) wygląda na puste "
                    f"({', '.join(blank_labels)}). Zachowuję je — użyj --skip-blank, żeby je pomijać "
                    "automatycznie w skryptach."
                )

    print_shop_info = None
    if config.print_shop:
        print_shop_info = {
            "Plik źródłowy": config.input_path.name,
            "Strona źródłowa": str(config.page_number),
            "Format arkusza": config.paper,
            "Orientacja": "poziomo" if paper_width_pt > paper_height_pt else "pionowo",
            "Zakładka": f"{config.overlap_mm:.1f} mm",
            "Liczba arkuszy": str(len(tiles) - len(skip_labels)),
            "Rozmiar arkusza": f"{pt_to_mm(paper_width_pt):.0f} x {pt_to_mm(paper_height_pt):.0f} mm",
            "Skala": "100% (bez przeskalowania)",
            "Data wygenerowania": date.today().isoformat(),
        }

    with Progress(console=console) as progress:
        task = progress.add_task("Zapisywanie arkuszy...", total=len(tiles))

        def _on_progress(done: int, total: int) -> None:
            progress.update(task, completed=done)

        write_tiled_pdf(
            input_path=config.input_path,
            output_path=config.output_path,
            tiles=tiles,
            paper_width_pt=paper_width_pt,
            paper_height_pt=paper_height_pt,
            page_number=config.page_number,
            draw_marks=config.marks,
            draw_cutlines=config.cutlines,
            draw_labels=config.labels,
            print_shop=config.print_shop,
            print_shop_info=print_shop_info,
            overlap_pt=overlap_pt,
            skip_labels=skip_labels,
            progress_callback=_on_progress,
        )

    console.print(f"[green]Gotowe:[/green] zapisano {output_path}")


if __name__ == "__main__":
    main()
