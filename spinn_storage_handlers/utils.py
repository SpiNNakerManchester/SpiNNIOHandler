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

import os


def file_length(f):
    """ The size of an open file.

    :param f: The file to get the size of
    :type f: file
    :return: The size of the file
    :rtype: int
    """
    # pylint: disable=broad-except
    try:
        # fstat() is fastest, but cannot guarantee it will work
        return os.fstat(f.fileno()).st_size
    except Exception:   # pragma: no cover
        current_pos = f.tell()
        f.seek(0, os.SEEK_SET)
        end_pos = f.tell()
        f.seek(current_pos)
        return end_pos
