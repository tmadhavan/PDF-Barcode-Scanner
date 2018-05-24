import os 
from PIL import Image
from pyzbar.pyzbar import decode, PyZbarError


# Iterate a list of images in a folder, and attempt to scan any barcodes that are present in the 
# image 
def scan_images(folder_to_scan: str, output_file_path: str, filetypes_to_decode: list=list(["png"])):
    """
    Look in a folder for images, then use ZBar to scan the images and detect any barcodes, outputting the barcode
    numbers to a text file

    :param folder_to_scan: The folder in which to search for images
    :param output_file_path: The output file to which detected barcode numbers will be written
    :param filetypes_to_decode: The image file type(s) to scan
    :return:
    """
    print(f'barcode_extractor.py scanning {folder_to_scan}')

    with open(output_file_path, 'w') as output_file:
        sorted_file_list = os.listdir(folder_to_scan)

        for file in sorted(sorted_file_list):
            absolute_path_to_file = os.path.join(folder_to_scan, file)
            if os.path.isfile(absolute_path_to_file) and file.endswith(tuple(filetypes_to_decode)):
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
