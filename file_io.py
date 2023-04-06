from os import listdir, path

def get_next_filename(basename, directory=".", digits=3):
    files = listdir(directory)
    files.sort()
    files.reverse()
    lowest_number = 0
    for file in files:
        if not path.isfile(file): continue
        if not file.startswith(basename): continue
        try:
            number = int(file.split('.')[0].strip(basename))
            if number < lowest_number: continue
        except ValueError:
            continue

        







