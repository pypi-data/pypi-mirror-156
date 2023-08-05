import argparse
import pkg_resources
from ._base import create


PACKAGES: [str] = None
WITHOUT_VERSION = False
FILENAME = None
include = False
DEV_PKGS = {"pip", "setuptools", "distribute", "wheel"}


def commands():
    global PACKAGES, WITHOUT_VERSION, FILENAME, DEV_PKGS
    
    parser = argparse.ArgumentParser(prog='freeze', description='A moderated pip freeze package.')
    
    parser.add_argument("--without-version", dest="without_version", action="store_true",
                        help="List of all installed packages without version.")

    parser.add_argument("-p", "--pkg", dest="pkg", metavar="", type=str,
                        help="List of packages name which separate with (,) comma.")

    parser.add_argument("-a", "--all", dest="all", action="store_true",
                        help="Do not skip these packages in the output: setuptools, distribute, wheel, pip")

    parser.add_argument("-o", "--output", dest="output", metavar="", type=str, default=False,
                        help="Use the order in the given requirements file and its comments when generating output.")

    args = parser.parse_args()
    
    if args.pkg:
        PACKAGES = [x.strip().lower() for x in args.pkg.split(",")]
        PACKAGES = [(pkg.project_name, pkg.version) for pkg in pkg_resources.working_set if pkg.project_name.lower() in PACKAGES]
    else:
        if args.all:
            PACKAGES = [(pkg.project_name, pkg.version) for pkg in pkg_resources.working_set]
        else:
            PACKAGES = [(pkg.project_name, pkg.version) for pkg in pkg_resources.working_set if pkg.project_name not in set(DEV_PKGS)]
    
    if args.output:
        FILENAME = args.output
    
    if args.without_version:
        WITHOUT_VERSION = args.without_version
    

def argparse_main():
    commands()
    create(PACKAGES, WITHOUT_VERSION, FILENAME)
