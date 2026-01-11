# pip install Pillow PyMuPDF
import subprocess
from pathlib import Path
import fitz

from PIL import Image


GR = '\033[92m'
RD = '\033[91m'
DYEL = '\033[33m'
BLD = '\033[1m'
UNDLN = '\033[4m'
DFLT = '\033[0m'
BL = '\033[94m'
STAND = '\033[39m'

errors = []


def tiff_to_jpg(input_path, output_path, nm):
    try:
        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'LA', 'PA'):
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)
            print(f"{GR}[{STAND}{nm}{GR}] Convert: {STAND}{Path(input_path).name} {GR}→ {STAND}{output_path.name}")
        Path(input_path).unlink()
    except Exception as e:
        print(f"\n{GR}[{DYEL}!{GR}] {RD}Ошибка при конвертации: {STAND}{e}")
        errors.append(f"\n{GR}[{DYEL}!{GR}] {RD}Ошибка при конвертации: {STAND}{e}")


def convert_djvu_to_tiff(input_path, nm):
    convert_options = [
        r"ddjvu_lib\ddjvu.exe",
        "-format=tiff",
        "-pages=1"
    ]

    output_name = f"{Path(input_path).stem}_001.tiff"
    output_path = str(Path(input_path).parent / output_name)
    command = convert_options + [str(input_path), output_path]

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print(f"{GR}[{STAND}{nm}{GR}] Сохранено: {STAND}{Path(output_path).name}")
            output_jpg = Path(output_path).parent / f"{Path(output_name).stem}.jpg"
            tiff_to_jpg(output_path, output_jpg, nm)
        else:
            print(f"\n{GR}[{DYEL}!{GR}] {RD}Ошибка при обработке {STAND}{input_path.name}:")
            errors.append(f"{GR}[{DYEL}!{GR}] {RD}Ошибка при обработке {STAND}{input_path.name}")
            print(f"{GR}Код возврата: {STAND}{process.returncode}")
            if stderr:
                print(f"{GR}Детали ошибки: {STAND}{stderr}")
    except Exception as e:
        print(f"\n{GR}[{DYEL}!{GR}] {RD}Исключение при обработке {STAND}{input_path.name}: {e}")
        errors.append(f"{GR}[{DYEL}!{GR}] {RD}Исключение при обработке {STAND}{input_path.name}")


def convert_pdf_to_jpg(pdf_path, nm):
    pdf_document = None
    try:
        pdf_document = fitz.open(pdf_path)
        if len(pdf_document) == 0:
            print(f"\n{GR}[{DYEL}!{GR}] {RD}PDF без страниц: {STAND}{pdf_path.name}")
            errors.append(f"{GR}[{DYEL}!{GR}] {RD}PDF без страниц: {STAND}{pdf_path.name}")
            pdf_document.close()
            return
        page = pdf_document[0]
        pix = page.get_pixmap()
        output_name = f"{pdf_path.stem}_001.jpg"
        output_path = pdf_path.parent / output_name
        pix.save(str(output_path))
        print(f"{GR}[{STAND}{nm}{GR}] Сохранено: {STAND}{output_path.name}")
        pdf_document.close()

    except Exception as e:
        print(f"\n{GR}[{DYEL}!{GR}] {RD}Ошибка при обработке {STAND}{pdf_path.name}: {e}".strip())
        errors.append(f"{GR}[{DYEL}!{GR}] {RD}Ошибка при обработке {STAND}{pdf_path.name}")
        if pdf_document:
            pdf_document.close()


def main():
    directory_path = Path(input("path >>> "))
    if not directory_path.exists() or not directory_path.is_dir():
        print(f"\n{GR}[{DYEL}!{GR}] {RD}Директория не найдена: {STAND}{directory_path}")
        exit(0)
    files = [fl for fl in Path(directory_path).iterdir() if
             Path(fl).suffix.lower() in [".djvu", ".djv", ".pdf"] and Path(fl).is_file()]
    len_files = len(files)
    for nm, file in enumerate(files, 1):
        if file.suffix in [".djvu", ".djv"]:
            convert_djvu_to_tiff(file, f"{nm}/{len_files}")
        elif file.suffix in [".pdf"]:
         convert_pdf_to_jpg(file, f"{nm}/{len_files}")
    if errors:
        print(f"{DYEL}\nОшибки:")
        for err in errors:
            print(f" - {err}")


if __name__ == "__main__":
    main()