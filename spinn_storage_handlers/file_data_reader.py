# Copyright (c) 2017 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinn_utilities.overrides import overrides
from .storage import _Storage
from .abstract_classes import (
    AbstractDataReader, AbstractContextManager)


class FileDataReader(AbstractDataReader, AbstractContextManager):
    """ A reader that can read data from a file.
    """

    __slots__ = [
        # the container for the file
        "_file_container"
    ]

    def __init__(self, filename):
        """
        :param filename: The file to read
        :type filename: str
        :raise spinn_storage_handlers.exceptions.DataReadException: \
            If the file cannot found or opened for reading
        """
        self._file_container = _Storage(filename, "rb")

    @overrides(AbstractDataReader.read)
    def read(self, n_bytes):
        return self._file_container.read(n_bytes)

    @overrides(AbstractDataReader.readall)
    def readall(self):
        return self._file_container.read_all()

    @overrides(AbstractDataReader.readinto)
    def readinto(self, data):
        return self._file_container.readinto(data)

    @overrides(AbstractDataReader.tell)
    def tell(self):
        return self._file_container.tell_read()

    @overrides(AbstractContextManager.close, extend_doc=False)
    def close(self):
        """ Closes the file.

        :rtype: None
        :raise spinn_storage_handlers.exceptions.DataReadException: \
            If the file cannot be closed
        """
        self._file_container.close()
