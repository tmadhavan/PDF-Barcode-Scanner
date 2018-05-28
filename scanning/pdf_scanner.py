import math
import os
import re
from PIL import Image
from pyzbar.pyzbar import decode, PyZbarError
from subprocess import CompletedProcess, run
from PyPDF2 import PdfFileReader

from exceptions.scannerexceptions import ScanError


def scan_pdf(path_to_pdf: str, output_file: str):
    end_page = PdfFileReader(path_to_pdf).getNumPages()
    output_folder = os.path.dirname(path_to_pdf)
    print("Output folder is: " + output_folder)
    output_file_path = os.path.join(output_folder, output_file)

    # Open the output file
    with open(output_file_path, 'w') as barcode_output_file:

        number_format = get_number_format(end_page)

        # Do the text conversion and parsing (much faster than the image conversion)
        pdf_text_output_file_name = "text_output.txt"
        pdf_to_text_conversion_command = ['pdftotext', path_to_pdf, pdf_text_output_file_name]
        pdf_convert_to_text_result: CompletedProcess = run(pdf_to_text_conversion_command, cwd=output_folder)

        if pdf_convert_to_text_result.returncode != 0:
            raise ScanError(scanned_file=path_to_pdf)

        pdf_text_output_file_path = os.path.join(output_folder, pdf_text_output_file_name)

        try:
            potential_barcodes = parse_potential_barcodes(pdf_text_output_file_path)
            if len(potential_barcodes) > 0:
                barcode_output_file.write("Potential barcodes from PDF -> text conversion: \n")
                barcode_output_file.writelines(potential_barcodes)
                barcode_output_file.write("\n\nPotential barcodes from PDF -> image scanning: \n")
        except OSError:
            print(f"Could not parse converted text file {pdf_text_output_file_path}")
            raise
        except Exception as ex:
            print(f"Uknown error occurred scanning {pdf_text_output_file_path}")
            raise
        finally:
            os.remove(pdf_text_output_file_path)

        # While we still have pages remaining
        for pageNumber in range(1, end_page + 1):
            print(f"Converting page {pageNumber}")

            # Convert the next page of the PDF using pdftoppm
            pdf_to_image_conversion_command = ['pdftoppm', path_to_pdf, output_file, '-png', '-r', '300', '-f',
                                      str(pageNumber), '-l', str(pageNumber)]

            pdf_to_image_result: CompletedProcess = run(pdf_to_image_conversion_command, cwd=output_folder)

            if pdf_to_image_result.returncode != 0:
                raise ScanError(scanned_file=path_to_pdf)

            # Get the filename with the correct number format (e.g. '1.png', '001.png', depending on total number of
            # pages. This is how pdftoppm numbers them and isn't configurable.
            converted_image_file_path = os.path.join(output_folder, f"{output_file}-{number_format.format(pageNumber)}.png")

            # Scan the created image
            # Open as a PIL image file and use pyzbar to detect barcodes
            # Append the barcode(s) to the output file
            try:
                with Image.open(converted_image_file_path) as img:
                    print(f'Scanning file: {converted_image_file_path}')
                    try:
                        decoded_image = decode(img)
                        for barcode in decoded_image:
                            barcode_output_file.write(barcode.data.decode('ascii'))
                            barcode_output_file.write('\n')

                        barcode_output_file.write('\n')
                        print(f'Scanned file: {converted_image_file_path}')
                    except PyZbarError:
                        print("Could not decode image {}".format(converted_image_file_path))
                        continue

                print(f"Removing scanned image: {converted_image_file_path}")
                os.remove(converted_image_file_path)

            except OSError:
                print(f"Error opening file for decoding ({converted_image_file_path}).")
                break

        print(f"Completed scanning {path_to_pdf}")


def get_number_format(number_of_pages) -> str:
    """
    Get the correct number formatting for pdftoppm's output numbering. E.g. a file with 10-99 pages will have output
    images named '01.png, 02.png, 03.png'; a file with 100-999 pages will output '001.png, 002.png, 003.png'. We need
    to use the same formatting for reading the images back in (and scanning them)

    :param number_of_pages: The total number of pages
    :return: A format string (e.g. '{:03}') to use for formatting these page numbers into filenames
    """
    formatted_number_length = int(math.log10(number_of_pages)) + 1
    return "{:0" + str(formatted_number_length) + "}"


# Really simple digit matching just to play around with first
barcode_regexes = {
    # Matches 'xxx xxx xxx' or 'xxx-xxx-xxx' formats (ONLY for boundary at the string start and end
    # (not word boundaries)i.e. a line with 'xx xxx xxx xx-xx-xx-xxx-xxx' will have NO matches at all.
    'General': r'^([0-9]+([-][0-9]+)*)$|^([0-9]+([ ][0-9]+)*)$',
    'EAN-8': '^(\d{8})?$',
    'EAN-13': '^(\d{13}|\d{14})$',  # Should be 13 digits, but some use 14 :-/
    'UPC': '^(\d{12})$'
}


def parse_potential_barcodes(text_file: str) -> list:

    potential_barcodes = []
    matcher = re.compile(barcode_regexes['General'])

    with open(text_file, encoding='utf8') as pdf_text:
        for line in pdf_text.readlines():
            matches = re.findall(matcher, line)
            for group in matches:
                for potential_barcode in group:
                    if len(potential_barcode) >= 8:
                        print(f"Appending {potential_barcode}")
                        potential_barcodes.append(potential_barcode + '\n')

    return potential_barcodes
