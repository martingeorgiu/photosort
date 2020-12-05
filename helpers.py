import os

def exists_or_create(folder):
    if os.path.exists(folder):
        return folder
    else:
        try:
            os.makedirs(folder)
            return folder
        except:
            raise NameError('Folder does not exist and cannot be created')

def is_dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def convert_coordinate_list(coordinate):
    return (float(coordinate[0]) + float(coordinate[1])/60 + float(coordinate[2])/(60*60))