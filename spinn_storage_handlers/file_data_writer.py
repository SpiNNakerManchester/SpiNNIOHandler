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

import io
from spinn_utilities.overrides import overrides
from .abstract_classes import AbstractDataWriter, AbstractContextManager
from .exceptions import DataWriteException


class FileDataWriter(AbstractDataWriter, AbstractContextManager):
    __slots__ = [
        # the file container
        "_file_container",
        "_filename"
    ]

    def __init__(self, filename):
        """
        :param filename: The file to write to
        :type filename: str
        :raise spinn_storage_handlers.exceptions.DataWriteException: \
            If the file cannot found or opened for writing
        """
        self._filename = filename
        try:
            self._file_container = io.open(filename, mode="w+b")
        except IOError as e:
            raise DataWriteException(str(e))

    @overrides(AbstractDataWriter.write)
    def write(self, data):
        self._file_container.write(data)

    @overrides(AbstractDataWriter.tell)
    def tell(self):
        self._file_container.flush()
        return self._file_container.tell()

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
        return self._filename
