import sys
import getopt
import pkg_resources


packages: [str] = None
without_version = False
file_name = None
DEV_PKGS = {"pip", "setuptools", "distribute", "wheel"}


# "no such option: {option}\n\n"
string: str = "Usage:\n  " \
              "freeze.py [options]\n\n" \
              "General Options:\n  " \
              "-h, --help:                 Show help.\n  " \
              "-r, --requirement <file>    Use the order in the given requirements file and its comments when generating output.\n  " \
              "-P, --pkg:                  List of packages name which separate with (,) comma.\n  " \
              "--all                       Do not skip these packages in the output: setuptools, distribute, wheel, pip\n  " \
              "--without-version           List of all installed packages without version"


def commands(argv):
    global packages, without_version, file_name

    try:
        opts, args = getopt.getopt(argv, "hPr:", ["pkg=", "help", "without-version", "all", "requirement"])
    except getopt.GetoptError:
        print(string)
        sys.exit(2)

    opt = [x for x, _ in opts]
    
    if not bool(opts) or (len(opt) <= 2 and "--without-version" in opt):
        packages = [pkg.project_name for pkg in pkg_resources.working_set]

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(string)
            sys.exit()
        elif opt in ("-P", "--pkg"):
            packages = [x.strip().lower() for x in arg.split(",")]
        elif opt == ("-r", "--requirement"):
            file_name = arg if bool(arg) else None
        elif opt == "--without-version":
            without_version = True
            

def getopt_main():
    commands(sys.argv[1:])

    for pkg in pkg_resources.working_set:
        if packages and pkg.project_name.lower() in packages:
            if without_version:
                print(f"{pkg.project_name}")
            else:
                print(f"{pkg.project_name}=={pkg.version}")
