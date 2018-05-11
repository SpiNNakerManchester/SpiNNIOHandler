import os
import pytest
from spinn_storage_handlers import BufferedTempfileDataStorage

testdata = bytearray(b"ABcd1234")
MANY_TEMP_FILES = 2000
# pylint: disable=protected-access


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
    for i in range(MANY_TEMP_FILES):
        b = BufferedTempfileDataStorage()
        assert b not in temps
        temps.append(b)
        s = str(i)
        assert len(s) > 0
        b.write(bytearray(s.encode('latin-1')))
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
            f.write(b"abcde")
        f.write(bytearray(b"abcde"))
        f.seek_write(3)
        f.write(bytearray(b"ba"))
        f.seek_read(1)

        # Flush the OS file pointer
        for b in [BufferedTempfileDataStorage()
                  for _ in range(MANY_TEMP_FILES)]:
            b.close()

        assert f.read(3) == b'bcb'
        assert f.eof() is False
        assert f.tell_read() == 4
        assert f.tell_write() == 5
        f.write(bytearray(b"f"))
        f.seek_read(0)
        b = bytearray(6)
        assert f.readinto(b) == 6
        assert b == b'abcbaf'
        assert f.eof() is True


def test_seeking():
    with BufferedTempfileDataStorage() as f:
        f.write(bytearray(b"abPQRcd"))
        f.seek_read(1, os.SEEK_SET)
        assert f.read(1) == b'b'
        f.seek_read(1, os.SEEK_CUR)
        assert f.read(1) == b'Q'
        f.seek_read(-2, os.SEEK_END)
        assert f.read(1) == b'c'
        assert f.eof() is False
        f.read(1)
        assert f.eof() is True
        with pytest.raises(IOError):
            f.seek_read(0, "no such flag")


def test_close_at_end():
    temps = [BufferedTempfileDataStorage() for _ in range(5)]
    files = [t._name for t in temps]
    for f in files:
        assert os.path.isfile(f) is True
    # Actually, this is installed as an exit handler...
    BufferedTempfileDataStorage._close_all()
    for f in files:
        assert os.path.isfile(f) is False
