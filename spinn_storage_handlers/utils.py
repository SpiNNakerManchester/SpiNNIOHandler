import os


def file_length(f):
    """The size of an open file.

    :param f: The file to get the size of
    :type f: file
    :return: The size of the file
    :rtype: int
    """
    try:
        # fstat() is fastest, but cannot guarantee it will work
        return os.fstat(f.fileno()).st_size
    except Exception:   # pragma: no cover
        current_pos = f.tell()
        f.seek(0, os.SEEK_SET)
        end_pos = f.tell()
        f.seek(current_pos)
        return end_pos
