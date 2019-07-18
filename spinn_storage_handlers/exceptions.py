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


class DataWriteException(Exception):
    """ An exception that indicates that there was an error writing\
        to the underlying medium
    """


class DataReadException(Exception):
    """ An exception that indicates that there was an error reading\
        from the underlying medium
    """


class BufferedBytearrayOperationNotImplemented(NotImplementedError):
    """ An exception that denotes that the operation required is unavailable\
        for a byteArray buffer
    """
