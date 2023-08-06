#! usr/bin/python3

from file_utils import parse_manifest, copy_tree
from tempfile import TemporaryDirectory
import os
import shutil
import argparse


def argparse_setup():

    parser = argparse.ArgumentParser()

    parser.add_argument(
                        "--manifest", "-m",
                        help="name/path to manifest file, defaults to the name manifest.* in the current directory",
                        action="store",
                        default="."
    )
    parser.add_argument(
                        "--release",
                        help="release number to be added to the output zip file",
                        action="store",
                        default="1.0.0"
    )
    return parser


def make_release(manifest: str, release="1.0.0"):

    manifest = parse_manifest(manifest)
    repo = os.path.abspath(os.curdir)

    with TemporaryDirectory() as direc:

        for x in manifest["directories"]:
            copy_tree(x, direc)

        for x in manifest["files"]:
            try:
                os.makedirs(os.path.join(direc, os.path.dirname(x)))
            except FileExistsError:
                pass
            shutil.copy(x, os.path.join(direc, x))

        shutil.make_archive("Releases/release" + release, 'zip', direc)


if __name__ == '__main__':
    parser = argparse_setup()
    args = parser.parse_args()
    make_release(args.manifest, args.release)
