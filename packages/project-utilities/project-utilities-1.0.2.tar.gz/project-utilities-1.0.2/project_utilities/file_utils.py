import glob 
import os
import sys 
import yaml
import json
import shutil


def find_files(directory: str, file: str, exit: bool() = False, recursive: bool() = True):

    error_message = "ERROR " + file + " not found !"
    files = []

    if recursive:
        files += glob.glob(os.path.join(directory, '**', file), recursive=recursive)
    else:
        files += glob.glob(os.path.join(directory, file), recursive=recursive)

    if len(files) == 0:
        if exit:
            sys.exit(error_message)
        else: 
            return error_message
    
    if len(files) == 1: 
        return files[0]
    
    else: 
        return files


def file_ext(path:str):

    file = os.path.basename(path)
    ext = file.split(".")[-1]
    return ext


def parse_manifest(path:str):
    """ 

        Parse a manifest file which contains the files/directories to be added to the release 
        Should be able to use XML, JSON, YAML etc 

    """

    if os.path.isdir(path):
        path = glob.glob(os.path.join(path, "manifest.*"))
        if type(path) is list:
            path = path[0]

    ext = file_ext(path)

    if ext == "yml" or "yaml":
        with open(path) as file:
            return yaml.safe_load(file)

    if ext == "json":
        with open(path) as file:
            return json.load(file)


def copy_tree(src: str, dst: str):

    root = os.path.abspath(os.curdir)
    dst = os.path.abspath(dst)
    os.chdir(src)

    dst = os.path.join(dst, src)
    try:
        os.makedirs(dst)
    except FileExistsError:
        pass

    for x in os.listdir(os.curdir):
        if os.path.isdir(x):
            copy_tree(x, dst)
        else:
            shutil.copy(x, dst)
    os.chdir(root)  # pull back out


if __name__ == '__main__':
    copy_tree("layer1", "layer2")
