import os
from io import BlockingIOError

from .abstract_classes \
    import AbstractBufferedDataStorage, AbstractContextManager
from .exceptions import DataReadException, DataWriteException
from .utils import file_length


class BufferedFileDataStorage(AbstractBufferedDataStorage,
                              AbstractContextManager):
    """ Data storage based on a temporary file with two pointers, one for\
        reading and one for writing.
    """

    __slots__ = [
        # ??????????????
        "_filename",

        # ??????????????
        "_read_pointer",

        # ??????????????
        "_write_pointer",

        # ?????????
        "_file",

        # Whether we must flush before we can rely on the file's contents
        # being accurate.
        "_flush_pending"
    ]

    def __init__(self, filename, mode):
        self._filename = filename
        self._read_pointer = 0
        self._write_pointer = 0
        self._flush_pending = False

        # open the file using the real handler
        try:
            self._file = open(filename, mode)
        except IOError as e:
            raise DataReadException(
                "unable to open file {0}; {1}".format(filename, e))

    def _flush(self):
        if self._flush_pending:
            self._file.flush()
        self._flush_pending = False

    def write(self, data):
        if not isinstance(data, (bytearray, str)):
            raise DataWriteException(
                "data to write is not in a suitable format (bytearray or "
                "string). Current data format: {0:s}".format(type(data)))

        self._file.seek(self._write_pointer)

        try:
            self._file.write(data)
            self._flush_pending = True
        except IOError as e:
            raise DataWriteException(
                "unable to write {0:d} bytes to file {1:s}: caused by {2}"
                .format(len(data), self._filename, e))

        self._write_pointer += len(data)

    def read(self, data_size):
        self._flush()
        self._file.seek(self._read_pointer)

        try:
            data = self._file.read(data_size)
        except BlockingIOError as e:   # pragma: no cover
            raise DataReadException(
                "unable to read {0:d} bytes from file {1:s}; {2}"
                .format(data_size, self._filename, e))

        self._read_pointer += len(data)
        return data

    def readinto(self, data):
        """ See \
            :py:meth:`spinn_storage_handlers.abstract_classes.AbstractBufferedDataStorage.readinto`
        """
        self._flush()
        self._file.seek(self._read_pointer)

        try:
            length = self._file.readinto(data)
        except BlockingIOError as e:   # pragma: no cover
            raise IOError(
                "unable to read {0:d} bytes from file {1:s}; {2}"
                .format(len(data), self._filename, e))

        self._read_pointer += length
        return length

    def read_all(self):
        self._flush()
        self._file.seek(0)
        data = self._file.read()
        self._read_pointer = self._file.tell()
        return data

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

    def seek_read(self, offset, whence=os.SEEK_SET):
        self._read_pointer = self.__seek(self._read_pointer, offset, whence)

    def seek_write(self, offset, whence=os.SEEK_SET):
        self._write_pointer = self.__seek(self._write_pointer, offset, whence)

    def tell_read(self):
        return self._read_pointer

    def tell_write(self):
        return self._write_pointer

    def eof(self):
        file_len = self._file_len
        return (file_len - self._read_pointer) <= 0

    def close(self):
        try:
            self._file.close()
        except Exception as e:   # pragma: no cover
            raise DataReadException(
                "file {0} cannot be closed; {1}".format(self._filename, e))

    @property
    def _file_len(self):
        """The size of the file.

        :return: The size of the file
        :rtype: int
        """
        self._flush()
        return file_length(self._file)

    @property
    def filename(self):
        """
        property method

        """
        return self._filename
