import helpers, argparse, os, datetime, click, exifread, sys

from shutil import copy2
from collections import defaultdict

NO_DATE = 'unknown'

class ImageToSort:
  def __init__(self, old_path, date, lat, long):
    self.old_path = old_path
    self.new_path = None
    self.date = date
    self.lat = lat
    self.long = long


if __name__ == "__main__":

    # parse input parameters
    argParse = argparse.ArgumentParser(description='Photosorting program',)
    argParse.add_argument('input_directory', type=helpers.is_dir_path, help='Input directory')
    argParse.add_argument('output_directory', type=helpers.exists_or_create, help='Output directory')
    argParse.add_argument('-x', '--deleteinput', action='store_true',help='Delete input files')
    argParse.add_argument('-m', '--generatehtml', action='store_true',help='Generate HTML')
    arguments = argParse.parse_args()

    input_directory = arguments.input_directory
    output_directiry = arguments.output_directory
    delete_input = arguments.deleteinput
    generate_html = arguments.generatehtml

    structure = defaultdict(list)

    # get all jpgs from input folder and add them to structure
    for file in os.listdir(input_directory):
        # filter out only jpgs
        if file.lower().endswith(".jpeg") or file.lower().endswith(".jpg"):
            input_file = os.path.join(input_directory, file)
            with open(input_file, 'rb') as f:
                # get exif data
                tags = exifread.process_file(f)
                tags_keys = tags.keys()

                lat = None
                long = None
                if 'GPS GPSLongitude' in tags_keys and 'GPS GPSLatitude' in tags_keys:
                    lat = tags['GPS GPSLatitude']
                    long = tags['GPS GPSLongitude']
                if 'EXIF DateTimeOriginal' in tags_keys:
                    # get date from the image
                    parsed_date = datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal'].values), '%Y:%m:%d %H:%M:%S')
                    structure[str(parsed_date.year)].append(ImageToSort(input_file, parsed_date, lat, long))
                else:
                    # no date found
                    structure[NO_DATE].append(ImageToSort(input_file, None, lat, long))
    
    if delete_input:
        delete_input = click.confirm('All the JPEG files will be removed, do you really want that?', default=True)

    #copy the images to output folder
    for year in structure:
        # sort images
        if year != NO_DATE:
            structure[year].sort(key=lambda img : img.date.timestamp())
        # create year dir if necessary
        year_dir = os.path.join(output_directiry, year)
        if not os.path.exists(year_dir):
            os.mkdir(year_dir)

        for i in range(len(structure[year])):
            sequence = i + 1
            file_name = f'{sequence:03}.jpg' if year == NO_DATE else f'{year}-{structure[year][i].date.month:02}-{structure[year][i].date.day:02}-{sequence:03}.jpg'
            structure[year][i].new_path = os.path.join(output_directiry, year, file_name)
            # copying the images to correct folders
            copy2(structure[year][i].old_path, structure[year][i].new_path)
            if delete_input:
                os.remove(structure[year][i].old_path)

    if generate_html:
        replace_string = ''
        for year in structure:
            for i in range(len(structure[year])):
                img = structure[year][i]
                if img.lat != None and img.long != None:
                    # adding imgs with coordinates to map
                    replace_string += f'L.marker([{helpers.convert_coordinate_list(img.lat.values)}, {helpers.convert_coordinate_list(img.long.values)}]).addTo(map).bindPopup(\'<img src="{img.new_path}" class="popup-img">\',{{minWidth:100}}).openPopup();'
        with open(os.path.join(sys.path[0], "template.html"), "r") as template:
            with open(os.path.join(output_directiry, "map.html"), "w") as generated_html:
                # generating the map.html from template
                generated_html.write(template.read().replace('REPLACE;',replace_string))

        
