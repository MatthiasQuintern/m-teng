from os import listdir, path

def add_zeros(v: int, digits=3):
    """
    return v as string, add leading zeros if len(str(v)) < digits
    """
    s = str(v)
    return '0' * (max(digits - len(s), 0)) + s


def get_next_filename(basename, directory=".", digits=3):
    """
    get the next filename (without extenstion).
    example:
        basename = file
        directory has file001, file002, file004
        -> return file005
    """
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
            lowest_number = number
        except ValueError:
            continue

    return basename + add_zeros(lowest_number)
