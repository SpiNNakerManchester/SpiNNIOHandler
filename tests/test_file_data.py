import pytest
from spinn_storage_handlers.file_data_reader import FileDataReader
from spinn_storage_handlers.file_data_writer import FileDataWriter
from spinn_storage_handlers.buffered_file_data_storage \
    import BufferedFileDataStorage


testdata = "ABcd1234"


@pytest.yield_fixture
def temp_dir(tmpdir):
    # Directory for data
    dir = tmpdir.mkdir("test_file_data")
    assert dir.check(exists=1)

    yield dir

    # Cleanup
    try:
        dir.remove(ignore_errors=True)
    except:
        pass
    assert dir.check(exists=0)


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

    bfds.write(bytearray(testdata))
    bfds.read_all()  # Force flush to the OS

    assert p.size() == len(testdata)
    assert bfds._file_len == len(testdata)
    assert bfds.read_all() == testdata

    bfds.close()

    assert p.check(exists=1)
