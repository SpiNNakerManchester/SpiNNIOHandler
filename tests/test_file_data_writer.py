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

import unittest
import inspect
import os.path
from spinn_storage_handlers import FileDataWriter


class TestFileDataWriter(unittest.TestCase):
    def setUp(self):
        self._dir = os.path.dirname(inspect.getfile(self.__class__))

    def _file(self, filename):
        return os.path.join(self._dir, "files_data_writer", filename)

    def test_write_one_byte(self):
        writer = FileDataWriter(self._file('txt_one_byte'))
        writer.write(bytearray([0]))
        writer.close()

        with open(self._file('txt_one_byte'), "r") as file_handle:
            self.assertEqual(file_handle.read(1), '\x00')
            self.assertEqual(file_handle.read(1), '')

    def test_write_five_bytes(self):
        writer = FileDataWriter(self._file('txt_5_bytes'))
        writer.write(bytearray([1, 2, 3, 4, 5]))
        writer.close()

        with open(self._file('txt_5_bytes'), "r") as file_handle:
            self.assertEqual(file_handle.read(1), '\x01')
            self.assertEqual(file_handle.read(1), '\x02')
            self.assertEqual(file_handle.read(1), '\x03')
            self.assertEqual(file_handle.read(1), '\x04')
            self.assertEqual(file_handle.read(1), '\x05')
            self.assertEqual(file_handle.read(1), '')

    def test_write_from_empty_file(self):
        writer = FileDataWriter(self._file('txt_empty'))
        writer.write(bytearray())
        writer.close()

        with open(self._file('txt_empty'), "r") as file_handle:
            self.assertEqual(file_handle.read(1), '')


if __name__ == '__main__':
    unittest.main()
