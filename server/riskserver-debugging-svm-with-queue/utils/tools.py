import os


def get_dir_file_number(path):
    return len(os.listdir(path))
