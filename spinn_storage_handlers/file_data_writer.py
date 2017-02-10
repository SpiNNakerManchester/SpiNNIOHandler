from spinn_storage_handlers.buffered_file_data_storage import \
    BufferedFileDataStorage
from spinn_storage_handlers.abstract_classes.abstract_data_writer import \
    AbstractDataWriter


class FileDataWriter(AbstractDataWriter):
    """
    :param filename: str The file to write to
    :raise spinn_storage_handlers.exceptions.DataReadException: If the\
        file cannot found or opened for reading
    """

    __slots__ = [
        # the file container
        "_file_container"
    ]

    def __init__(self, filename):
        self._file_container = BufferedFileDataStorage(filename, "w+b")

    def write(self, data):
        """ See \
            :py:meth:`data_specification.abstract_data_writer.AbstractDataWriter.write`
        """
        self._file_container.write(data)

    def tell(self):
        """ Returns the position of the file cursor

        :return: Position of the file cursor
        :rtype: int
        """
        return self._file_container.tell_write()

    def close(self):
        """ Closes the file

        :rtype: None
        :raise spinn_storage_handlers.exceptions.DataWriteException: If the\
                    file cannot be closed
        """
        self._file_container.close()

    @property
    def filename(self):
        """
        property method
        """
        return self._file_container.filename
