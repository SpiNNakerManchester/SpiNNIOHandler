import atexit
import os
import tempfile
from spinn_storage_handlers.abstract_classes \
    import AbstractBufferedDataStorage, AbstractContextManager


_LRU = list()
_LRU_MAX = 100


class _SimpleFileWrapper(object):
    def __init__(self, filename):
        global _LRU
        self._file = open(filename, "w+b")
        _LRU.append(self)
        if len(_LRU) > _LRU_MAX:
            trim, _LRU = _LRU[:len(_LRU)-_LRU_MAX], _LRU[-_LRU_MAX:]
            for f in trim:
                f.close()

    def close(self):
        self._file.close()
        try:
            _LRU.remove(self)
        except ValueError:
            pass

    def read(self, size=None):
        try:
            _LRU.remove(self)
        except ValueError:
            pass
        _LRU.append(self)
        if size is None:
            return self._file.read()
        else:
            return self._file.read(size)

    def readinto(self, buffer):  # @ReservedAssignment
        try:
            _LRU.remove(self)
        except ValueError:
            pass
        _LRU.append(self)
        return self._file.readinto(buffer)

    def write(self, str):  # @ReservedAssignment
        try:
            _LRU.remove(self)
        except ValueError:
            pass
        _LRU.append(self)
        self._file.write(str)

    def seek(self, a, b=None):
        if b is None:
            self._file.seek(a)
        else:
            self._file.seek(a, b)

    def tell(self):
        return self._file.tell()


class BufferedTempfileDataStorage(AbstractBufferedDataStorage,
                                  AbstractContextManager):
    """Data storage based on a temporary file with two pointers, one for
    reading and one for writing.
    """

    __slots__ = [
        # ??????????????
        "_file_size",

        # ??????????????
        "_read_pointer",

        # ??????????????
        "_write_pointer",

        # ?????????
        "_file",
        "_name"
    ]

    _ALL = list()

    def __init__(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        self._name = f.name
        f.close()
        
        self._file = _SimpleFileWrapper(self._name)
        self._file_size = 0
        self._read_pointer = 0
        self._write_pointer = 0
        BufferedTempfileDataStorage._ALL.append(self)

    @property
    def _handle(self):
        """A handle to the file that we can actually read or write through.
        """
        if self._file not in _LRU:
            self._file = _SimpleFileWrapper(self._name)
        return self._file

    def write(self, data):
        if not isinstance(data, bytearray):
            raise
        f = self._handle
        f.seek(self._write_pointer)
        f.write(data)
        self._file_size += len(data)
        self._write_pointer += len(data)

    def read(self, data_size):
        f = self._handle
        f.seek(self._read_pointer)
        data = f.read(data_size)
        self._read_pointer += data_size
        return bytearray(data)

    def readinto(self, data):
        f = self._handle
        f.seek(self._read_pointer)
        data_size = f.readinto(data)
        self._read_pointer += data_size
        return data_size

    def read_all(self):
        f = self._handle
        f.seek(0)
        data = f.read()
        self._read_pointer = f.tell()
        return bytearray(data)

    def seek_read(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._read_pointer = offset
        elif whence == os.SEEK_CUR:
            self._read_pointer += offset
        elif whence == os.SEEK_END:
            self._read_pointer = self._file_size - abs(offset)

        if self._read_pointer < 0:
            self._read_pointer = 0

        file_len = self._file_len
        if self._read_pointer > file_len:
            self._read_pointer = file_len

    def seek_write(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._write_pointer = offset
        elif whence == os.SEEK_CUR:
            self._write_pointer += offset
        elif whence == os.SEEK_END:
            self._write_pointer = self._file_size - abs(offset)

        if self._write_pointer < 0:
            self._write_pointer = 0

        file_len = self._file_len
        if self._write_pointer > file_len:
            self._write_pointer = file_len

    def tell_read(self):
        return self._read_pointer

    def tell_write(self):
        return self._write_pointer

    def eof(self):
        file_len = self._file_len
        return (file_len - self._read_pointer) <= 0

    def close(self):
        if self._file in _LRU:
            self._file.close()
        BufferedTempfileDataStorage._ALL.remove(self)
        os.unlink(self._name)

    @property
    def _file_len(self):
        """ The size of the file

        :return: The size of the file
        :rtype: int
        """
        f = self._handle
        current_pos = f.tell()
        f.seek(0, 2)
        end_pos = f.tell()
        f.seek(current_pos)
        return end_pos

    @staticmethod
    def close_all():
        # Copy!
        alltoclose = list(BufferedTempfileDataStorage._ALL)
        for f in alltoclose:
            f.close()


atexit.register(BufferedTempfileDataStorage._close_them_all)
