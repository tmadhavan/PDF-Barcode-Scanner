import os 
import io
from PIL import Image
from pyzbar.pyzbar import decode, PyZbarError


# Iterate a list of images in a folder, and attempt to scan any barcodes that are present in the 
# image 
def scan_images(folder: str, output_filename: str, filetype_to_decode: str="png"):

    print(f'extractor.py scanning {folder}')

    # Put the output text file in the same folder as the one we're scanning
    absolute_path_to_output_file = os.path.join(folder, output_filename)

    with open(absolute_path_to_output_file, 'w') as output_file:
        sorted_file_list = os.listdir(folder)

        for file in sorted(sorted_file_list):
            absolute_path_to_file = os.path.join(folder, file)
            if os.path.isfile(absolute_path_to_file) and file.endswith(f'.{filetype_to_decode}'):
                output_file.write(f'\n\n{file}\n')
                
                # Open as a PIL image file and use pyzbar to detect barcodes 
                with Image.open(absolute_path_to_file) as img:
                    print(f'Scanning file: {absolute_path_to_file}')
                    try:
                        decoded_image = decode(img)
                        for barcode in decoded_image:
                            output_file.write(barcode.data.decode('ascii'))
                            output_file.write('\n')
                        print(f'Scanned file: {absolute_path_to_file}')
                    except PyZbarError: 
                        print("Could not decode image {}".format(absolute_path_to_file))
                        continue
