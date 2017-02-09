# import py.test
from spinn_storage_handlers.buffered_tempfile_data_storage \
    import BufferedTempfileDataStorage


testdata = bytearray("ABcd1234")


def test_readwrite_tempfile_buffer(tmpdir):
    btds = BufferedTempfileDataStorage()
    assert btds is not None
    assert btds._file_len == 0
    btds.write(testdata)
    assert btds._file_len == len(testdata)
    assert btds.read_all() == testdata
    btds.close()
