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

import pytest
from spinn_storage_handlers.exceptions import DataReadException
from spinn_storage_handlers import FileDataReader, FileDataWriter

testdata = bytearray(b"ABcd1234")
# pylint: disable=redefined-outer-name, broad-except, protected-access


@pytest.yield_fixture
def temp_dir(tmpdir):
    # Directory for data
    thedir = tmpdir.mkdir("test_file_data")
    assert thedir.check(exists=1)

    yield thedir

    # Cleanup
    try:
        thedir.remove(ignore_errors=True)
    except Exception:
        pass
    assert thedir.check(exists=0)


def test_read_file(temp_dir):
    p = temp_dir.join("test_read_file.txt")
    p.write_binary(testdata)
    fdr = FileDataReader(str(p))

    assert fdr is not None
    assert len(fdr.readall()) == len(testdata)

    fdr.close()


def test_write_file(temp_dir):
    p = temp_dir.join("test_write_file.txt")
    fdw = FileDataWriter(str(p))

    assert str(p) == fdw.filename

    fdw.write(testdata)
    fdw.close()
    content = p.read_binary()

    assert content is not None
    assert len(content) == len(testdata)


def test_no_such_file(temp_dir):
    p = temp_dir.join("test_no_such_file.txt")
    with pytest.raises(DataReadException):
        FileDataReader(str(p))


def test_readonly(temp_dir):
    p = temp_dir.join("test_readonly.txt")
    open(str(p), "w").close()
    with FileDataReader(str(p)) as f:
        assert f.read(100) == b""
        assert f.tell() == 0
        assert f.readinto(bytearray(100)) == 0
        assert f.tell() == 0
        assert f.readall() == b""


def test_writeonly(temp_dir):
    p = temp_dir.join("test_writeonly.txt")
    with FileDataWriter(str(p)) as f:
        assert f.tell() == 0
        f.write(b"abcde")
        assert f.tell() == 5
