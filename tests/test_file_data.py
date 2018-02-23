import os
import pytest
from spinn_storage_handlers.exceptions import DataReadException,\
    DataWriteException
from spinn_storage_handlers \
    import FileDataReader, FileDataWriter, BufferedFileDataStorage

testdata = bytearray("ABcd1234")


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


def test_readwrite_file_buffer(temp_dir):
    p = temp_dir.join("test_readwrite_file_buffer.txt")
    assert p.check(exists=0)

    bfds = BufferedFileDataStorage(str(p), "w+b")

    assert p.check(exists=1)
    assert p.size() == 0
    assert bfds is not None
    assert bfds._file_len == 0

    bfds.write(testdata)
    bfds.read_all()  # Force flush to the OS

    assert p.size() == len(testdata)
    assert bfds._file_len == len(testdata)
    assert bfds.read_all() == testdata

    bfds.close()

    assert p.check(exists=1)


def test_no_such_file(temp_dir):
    p = temp_dir.join("test_no_such_file.txt")
    with pytest.raises(DataReadException):
        BufferedFileDataStorage(str(p), "r")
    with pytest.raises(DataReadException):
        FileDataReader(str(p))


def test_readonly(temp_dir):
    p = temp_dir.join("test_readonly.txt")
    open(str(p), "w").close()
    with BufferedFileDataStorage(str(p), "r") as f:
        with pytest.raises(DataWriteException):
            f.write("foo")
        assert f.read(100) == ""
        f.seek_read(0)
        b = bytearray(100)
        assert f.readinto(b) == 0
    with FileDataReader(str(p)) as f:
        assert f.read(100) == ""
        assert f.tell() == 0
        assert f.readinto(bytearray(100)) == 0
        assert f.tell() == 0
        assert f.readall() == ""


def test_writeonly(temp_dir):
    p = temp_dir.join("test_writeonly.txt")
    with BufferedFileDataStorage(str(p), "w") as f:
        f.write("foo")
        with pytest.raises(IOError):
            f.read(100)
        f.seek_write(0)
        with pytest.raises(DataWriteException):
            f.write(12345)
    with FileDataWriter(str(p)) as f:
        assert f.tell() == 0
        f.write("abcde")
        assert f.tell() == 5


def test_seeking(temp_dir):
    p = temp_dir.join("test_seeking.txt")
    with BufferedFileDataStorage(str(p), "w+") as f:
        f.write("abPQRcd")
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
