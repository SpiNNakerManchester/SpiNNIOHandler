import os
from spinn_utilities.overrides import overrides
from spinn_storage_handlers.abstract_classes \
    import AbstractContextManager, AbstractBufferedDataStorage
from spinn_storage_handlers.exceptions import \
    BufferedBytearrayOperationNotImplemented, DataWriteException


class BufferedBytearrayDataStorage(AbstractBufferedDataStorage,
                                   AbstractContextManager):
    """ Data storage based on a bytearray buffer with two pointers,\
        one for reading and one for writing.
    """

    __slots__ = [
        # ?????????????
        "_data_storage",

        # ??????????
        "_read_pointer",

        # ??????????
        "_write_pointer"
    ]

    def __init__(self):
        self._data_storage = bytearray()
        self._read_pointer = 0
        self._write_pointer = 0

    @overrides(AbstractBufferedDataStorage.write)
    def write(self, data):
        if not isinstance(data, bytearray):
            raise DataWriteException("can only write bytearrays")
        self._data_storage[
            self._write_pointer:self._write_pointer + len(data)] = data
        self._write_pointer += len(data)

    @overrides(AbstractBufferedDataStorage.read)
    def read(self, data_size):
        end_ptr = self._read_pointer + data_size
        data = self._data_storage[self._read_pointer:end_ptr]
        self._read_pointer += len(data)
        return data

    @overrides(AbstractBufferedDataStorage.readinto)
    def readinto(self, data):
        raise BufferedBytearrayOperationNotImplemented("operation unavailable")

    @overrides(AbstractBufferedDataStorage.read_all)
    def read_all(self):
        return self._data_storage

    def __seek(self, pointer, offset, whence):
        if whence == os.SEEK_SET:
            pointer = offset
        elif whence == os.SEEK_CUR:
            pointer += offset
        elif whence == os.SEEK_END:
            pointer = len(self._data_storage) - abs(offset)
        else:
            raise IOError("unrecognised 'whence'")
        return max(min(pointer, len(self._data_storage)), 0)

    @overrides(AbstractBufferedDataStorage.seek_read)
    def seek_read(self, offset, whence=os.SEEK_SET):
        self._read_pointer = self.__seek(self._read_pointer, offset, whence)

    @overrides(AbstractBufferedDataStorage.seek_write)
    def seek_write(self, offset, whence=os.SEEK_SET):
        self._write_pointer = self.__seek(self._write_pointer, offset, whence)

    @overrides(AbstractBufferedDataStorage.tell_read)
    def tell_read(self):
        return self._read_pointer

    @overrides(AbstractBufferedDataStorage.tell_write)
    def tell_write(self):
        return self._write_pointer

    @overrides(AbstractBufferedDataStorage.eof)
    def eof(self):
        return (len(self._data_storage) - self._read_pointer) <= 0

    @overrides(AbstractBufferedDataStorage.close)
    def close(self):
        self._data_storage = None
        self._read_pointer = 0
        self._write_pointer = 0
