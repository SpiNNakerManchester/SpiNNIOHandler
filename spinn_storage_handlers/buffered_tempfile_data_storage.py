import atexit
import os
import pylru
import tempfile
from spinn_utilities.overrides import overrides
from .abstract_classes \
    import AbstractBufferedDataStorage, AbstractContextManager
from .utils import file_length


# Maximum number of entries in the underlying LRU cache
_LRU_MAX = 100


class BufferedTempfileDataStorage(AbstractBufferedDataStorage,
                                  AbstractContextManager):
    """ Data storage based on a temporary file with two pointers, one for\
        reading and one for writing. Under the covers, it actually opens and\
        closes the temporary file as it chooses in order to limit the number\
        of file descriptors in use.
    """

    __slots__ = [
        # Where in the file any reads will occur
        "_read_pointer",

        # Where in the file any writes will occur
        "_write_pointer",

        # The name of the temporary file
        "_name",

        # Whether we need to do a flush before proceeding with reads
        "_flush_pending"
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
        self._read_pointer = 0
        self._write_pointer = 0
        self._flush_pending = False
        self._ALL.add(self)

    @property
    def _handle(self):
        """ A handle to the file that we can actually read or write through.

        :rtype: file
        """
        if self._name in self._LRU:
            return self._LRU[self._name]
        new = open(self._name, "r+b")
        self._LRU[self._name] = new
        return new

    @overrides(AbstractBufferedDataStorage.write)
    def write(self, data):
        if not isinstance(data, (bytes, bytearray)):
            raise IOError("can only write bytearrays")
        f = self._handle
        f.seek(self._write_pointer)
        f.write(data)
        self._flush_pending = True
        self._write_pointer += len(data)

    def _flush(self, f=None):
        if f is None:
            f = self._handle
        if self._flush_pending:
            f.flush()
        self._flush_pending = False

    @overrides(AbstractBufferedDataStorage.read)
    def read(self, data_size):
        f = self._handle
        self._flush(f)
        f.seek(self._read_pointer)
        data = f.read(data_size)
        self._read_pointer += len(data)
        return bytearray(data)

    @overrides(AbstractBufferedDataStorage.readinto)
    def readinto(self, data):
        f = self._handle
        self._flush(f)
        f.seek(self._read_pointer)
        data_size = f.readinto(data)
        self._read_pointer += data_size
        return data_size

    @overrides(AbstractBufferedDataStorage.read_all)
    def read_all(self):
        f = self._handle
        self._flush(f)
        f.seek(0)
        data = f.read()
        self._read_pointer = f.tell()
        return bytearray(data)

    def __seek(self, pointer, offset, whence):
        if whence == os.SEEK_SET:
            pointer = offset
        elif whence == os.SEEK_CUR:
            pointer += offset
        elif whence == os.SEEK_END:
            pointer = self._file_len - abs(offset)
        else:
            raise IOError("unrecognised 'whence'")
        return max(min(pointer, self._file_len), 0)

    @overrides(AbstractBufferedDataStorage.seek_read)
    def seek_read(self, offset, whence=os.SEEK_SET):
        self._flush()
        self._read_pointer = self.__seek(self._read_pointer, offset, whence)

    @overrides(AbstractBufferedDataStorage.seek_write)
    def seek_write(self, offset, whence=os.SEEK_SET):
        self._flush()
        self._write_pointer = self.__seek(self._write_pointer, offset, whence)

    @overrides(AbstractBufferedDataStorage.tell_read)
    def tell_read(self):
        return self._read_pointer

    @overrides(AbstractBufferedDataStorage.tell_write)
    def tell_write(self):
        return self._write_pointer

    @overrides(AbstractBufferedDataStorage.eof)
    def eof(self):
        file_len = self._file_len
        return (file_len - self._read_pointer) <= 0

    @overrides(AbstractBufferedDataStorage.close)
    def close(self):
        # Don't need to flush; any pending writes are auto-flushed
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
        self._flush(f)
        return file_length(f)

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
