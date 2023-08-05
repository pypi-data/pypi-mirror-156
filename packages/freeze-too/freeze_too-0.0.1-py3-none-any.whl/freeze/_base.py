def create(packages, without_version, filename):
    if filename:
        with open(filename, "w") as file:
            [file.write(pkg[0]+"\n") if without_version else file.write("==".join(pkg)+"\n") for pkg in packages]
    else:
        [print(pkg[0]) if without_version else print("==".join(pkg)) for pkg in packages]
