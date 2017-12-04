import atexit
import os
import pylru
import tempfile
from spinn_storage_handlers.abstract_classes \
    import AbstractBufferedDataStorage, AbstractContextManager


# Maximum number of entries in the underlying LRU cache
_LRU_MAX = 100


class BufferedTempfileDataStorage(AbstractBufferedDataStorage,
                                  AbstractContextManager):
    """Data storage based on a temporary file with two pointers, one for
    reading and one for writing.
    """

    __slots__ = [
        # The current (believed) size of the file
        "_file_size",

        # Where in the file any reads will occur
        "_read_pointer",

        # Where in the file any writes will occur
        "_write_pointer",

        # The name of the temporary file
        "_name"
    ]

    # Collection of all current BufferedTempfileDataStorages so that the exit
    # handler can clean up correctly.
    _ALL = set()

    # Least-recently-used cache that manages when to auto-close the system
    # file handles.
    _LRU = None

    def __init__(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        self._name = f.name
        f.close()
        self._handle.seek(0)
        self._file_size = 0
        self._read_pointer = 0
        self._write_pointer = 0
        self._ALL.add(self)

    @property
    def _handle(self):
        """A handle to the file that we can actually read or write through.

        :rtype: file
        """
        if self._name in self._LRU:
            return self._LRU[self._name]
        new = open(self._name, "r+b")
        self._LRU[self._name] = new
        return new

    def write(self, data):
        if not isinstance(data, bytearray):
            raise IOError("can only write bytearrays")
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
        if self._name in self._LRU:
            del self._LRU[self._name]
        self._ALL.remove(self)
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

    @classmethod
    def initialise(cls, lru_max):
        cls._LRU = pylru.lrucache(lru_max, cls._clean_file)
        atexit.register(cls._close_all)

    @staticmethod
    def _clean_file(_, f):
        f.close()

    @classmethod
    def _close_all(cls):
        # Copy!
        alltoclose = list(cls._ALL)
        for f in alltoclose:
            f.close()


# Set up the class's system entanglements
BufferedTempfileDataStorage.initialise(_LRU_MAX)
