import argparse
import os
import git
import sys


def argparse_setup():

    parser = argparse.ArgumentParser()

    parser.add_argument(
                        "--name", "-n",
                        help="name of project (for project folder, if not given assumed directory is already made)",
                        action="store",
                        required=False,
    )

    parser.add_argument(
                        "--style", "-s",
                        help="style of the project i.e. rust project, python project, python package",
                        action="store",
                        default="default",
    )

    parser.add_argument(
                        "--virtual-env",
                        help="name of virtual environment package e.g. conda, virtualenv, venv",
                        action="store",
    )

    parser.add_argument(
                        "--no-git",
                        help="whether to initialise a git repository of not",
                        action="store_true",
    )

    parser.add_argument(
                        "--dir", "-d",
                        help="directory where project is to be initialised, defaults to current directory",
                        default="."
    )

    parser.add_argument(
                        "--git-clone",
                        help="give a URL to a git repo to be cloned",
                        action="store",
                        required=False,
    )
    return parser


if __name__ == "__main__":
    parser = argparse_setup()
    args = parser.parse_args()

    name = args.name
    no_git = args.no_git
    virtualenv = args.virtual_env
    style = args.style
    dir = args.dir
    git_url = args.git_clone

    if os.path.isdir(dir):
        os.chdir(dir)
    else:
        os.mkdir(dir)

    if name is not None:
        os.mkdir(name)
        os.chdir(name)

    if not no_git:
        if git_url is not None:
            git.Repo.clone_from(git_url)
            sys.exit(0)

        else:
            git.Repo.init(os.curdir)

    if style == "default":
        os.mkdir("src")
        os.mkdir("docs")
        os.mkdir("scripts")
        os.mkdir("tests")

        with open(".gitignore", "w") as f:
            f.write("__pycache__\n")
            f.write(".idea\n")
            f.write(".vscode\n")

    elif style == "package":
        os.mkdir(name)
        os.mkdir("tests")
        os.mkdir("docs")

        open("LICENSE", "x")
        open("README.md", "x")
        open("setup.py", "x")
        with open(".gitignore", "w") as f:
            f.write("__pycache__\n")
            f.write(".idea\n")
            f.write(".vscode\n")

        os.chdir(name)

        open("__init__.py", "x")

    else:
        sys.exit("ERROR: style argument given is not recognised")



