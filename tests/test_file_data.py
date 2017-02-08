# import py.test
from spinn_storage_handlers.file_data_reader import FileDataReader
from spinn_storage_handlers.file_data_writer import FileDataWriter


def test_read_file(tmpdir):
    p = tmpdir.mkdir("spinn_storage_handlers").join("data.txt")
    p.write_binary("ABcd1234")
    fdr = FileDataReader(str(p))
    assert fdr is not None
    assert len(fdr.readall()) == 8
    fdr.close()


def test_write_file(tmpdir):
    p = tmpdir.mkdir("spinn_storage_handlers").join("data.txt")
    fdw = FileDataWriter(str(p))
    assert str(p) == fdw.filename
    fdw.write("ABcd1234")
    fdw.close()
    content = p.read_binary()
    assert content is not None
    assert len(content) == 8
