# import py.test
from spinn_storage_handlers.file_data_reader import FileDataReader


def test_read_file(tmpdir):
    p = tmpdir.mkdir("spinn_storage_handlers").join("data.txt")
    p.write_binary("ABcd1234")
    fdr = FileDataReader(str(p))
    assert fdr is not None
    assert len(fdr.readall()) == 8
