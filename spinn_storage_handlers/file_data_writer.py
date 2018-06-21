from .buffered_file_data_storage import BufferedFileDataStorage
from spinn_storage_handlers.abstract_classes import \
    AbstractDataWriter, AbstractContextManager
from spinn_utilities.overrides import overrides


class FileDataWriter(AbstractDataWriter, AbstractContextManager):
    __slots__ = [
        # the file container
        "_file_container"
    ]

    def __init__(self, filename):
        """
        :param filename: The file to write to
        :type filename: str
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If the file cannot found or opened for writing
        """
        self._file_container = BufferedFileDataStorage(filename, "w+b")

    @overrides(AbstractDataWriter.write)
    def write(self, data):
        self._file_container.write(data)

    @overrides(AbstractDataWriter.tell)
    def tell(self):
        return self._file_container.tell_write()

    @overrides(AbstractContextManager.close, extend_doc=False)
    def close(self):
        """ Closes the file.

        :rtype: None
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If the file cannot be closed
        """
        self._file_container.close()

    @property
    def filename(self):
        """ The name of the file that is being written to.
        """
        return self._file_container.filename
