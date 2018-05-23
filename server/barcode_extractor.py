import os 
import io
from PIL import Image
from pyzbar.pyzbar import decode, PyZbarError


# Iterate a list of images in a folder, and attempt to scan any barcodes that are present in the 
# image 
def scan_images(folder_to_scan: str, output_file_path: str, filetype_to_decode: str= "png"):

    print(f'barcode_extractor.py scanning {folder_to_scan}')

    with open(output_file_path, 'w') as output_file:
        sorted_file_list = os.listdir(folder_to_scan)

        for file in sorted(sorted_file_list):
            absolute_path_to_file = os.path.join(folder_to_scan, file)
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
