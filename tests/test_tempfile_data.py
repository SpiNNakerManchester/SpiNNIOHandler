# import py.test
from spinn_storage_handlers import BufferedTempfileDataStorage
import os
import pytest

testdata = bytearray("ABcd1234")
MANY_TEMP_FILES = 2000


def test_readwrite_tempfile_buffer():
    btds = BufferedTempfileDataStorage()
    assert btds is not None
    assert btds._file_len == 0
    btds.write(testdata)
    assert btds._file_len == len(testdata)
    assert btds.read_all() == testdata
    btds.close()


def test_lots_of_tempfiles():
    temps = list()
    for i in xrange(MANY_TEMP_FILES):
        b = BufferedTempfileDataStorage()
        assert b not in temps
        temps.append(b)
        s = str(i)
        assert len(s) > 0
        b.write(bytearray(s))
        assert b._write_pointer > 0
    assert len(temps) == MANY_TEMP_FILES
    vals = list()
    for t in temps:
        vals.append(int(t.read_all()))
        assert t._read_pointer != 0
    assert vals == sorted(list(vals))
    for t in temps:
        flnm = t._name
        assert os.path.isfile(flnm)
        t.close()
        assert not os.path.isfile(flnm)


def test_basic_ops():
    with BufferedTempfileDataStorage() as f:
        with pytest.raises(IOError):
            f.write("abcde")
        f.write(bytearray("abcde"))
        f.seek_write(3)
        f.write(bytearray("ba"))
        f.seek_read(1)

        # Flush the OS file pointer
        for b in [BufferedTempfileDataStorage()
                  for _ in xrange(MANY_TEMP_FILES)]:
            b.close()

        assert f.read(3) == 'bcb'
        assert f.eof() is False
        assert f.tell_read() == 4
        assert f.tell_write() == 5
        f.write(bytearray("f"))
        f.seek_read(0)
        b = bytearray(6)
        assert f.readinto(b) == 6
        assert b == 'abcbaf'
        assert f.eof() is True


def test_seeking():
    with BufferedTempfileDataStorage() as f:
        f.write(bytearray("abPQRcd"))
        f.seek_read(1, os.SEEK_SET)
        assert f.read(1) == 'b'
        f.seek_read(1, os.SEEK_CUR)
        assert f.read(1) == 'Q'
        f.seek_read(-2, os.SEEK_END)
        assert f.read(1) == 'c'
        assert f.eof() is False
        f.read(1)
        assert f.eof() is True
        with pytest.raises(IOError):
            f.seek_read(0, "no such flag")
