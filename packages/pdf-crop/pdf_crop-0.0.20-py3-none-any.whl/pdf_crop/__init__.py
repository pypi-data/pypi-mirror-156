import os
from os import walk

from rich.console import Console
from rich.table import Table
from pdf_crop.crop_pymupdf import PymuPDFCrop
from pdf_crop.helper import rect_str


def crop(input_file, page_option: list, show_summary=True, crop_from='center'):
    table = Table(title="PDF Crop Summary", leading=0)
    table.add_column("Page No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("MediaBox", justify="right", style="magenta")
    table.add_column("CropBox", justify="right", style="magenta")
    table.add_column("Output", justify="right", style="green")
    table_data = list()

    space, threshold = (5, 0.008)
    for option in page_option:
        page_no, output_file = option[:2]
        if len(option) > 2:
            space = option[2]
        if len(option) > 3:
            threshold = option[3]
        pdf_crop = PymuPDFCrop(input_file=input_file, space=space, threshold=threshold, crop_from=crop_from)
        output_file, media_box, crop_box = pdf_crop.crop(page_no, output_file=output_file, crop_box=None)
        table_data.append((str(option[0]), rect_str(media_box), rect_str(crop_box), output_file))
    for row in table_data:
        table.add_row(*row)
    if show_summary:
        console = Console()
        console.print(table)
    return table_data


def crop_single_page_files(input_folder, output_folder, show_summary=True, space=5, threshold=0.008):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    pdfs = []
    for (dirpath, dirnames, filenames) in walk(input_folder):
        pdfs.extend(filenames)
        break
    summary = list()
    for f in pdfs:
        info = crop(f"{input_folder}/{f}",[(0, f"{output_folder}/{f}", 6), space, threshold], show_summary=False)
        summary.append((f"{input_folder}/{f}", *info[0][1:]))

    table = Table(title="PDF Crop Summary", leading=0)
    table.add_column("Input", justify="right", style="cyan", no_wrap=True)
    table.add_column("MediaBox", justify="right", style="magenta")
    table.add_column("CropBox", justify="right", style="magenta")
    table.add_column("Output", justify="right", style="green")
    for row in summary:
        table.add_row(*row)
    if show_summary:
        console = Console()
        console.print(table)