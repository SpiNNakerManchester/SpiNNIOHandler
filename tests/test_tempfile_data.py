# import py.test
from spinn_storage_handlers.buffered_tempfile_data_storage \
    import BufferedTempfileDataStorage


def test_readwrite_tempfile_buffer(tmpdir):
    btds = BufferedTempfileDataStorage()
    assert btds is not None
    assert btds._file_len == 0
    btds.write(bytearray("ABcd1234"))
    assert btds._file_len == 8
    assert btds.read_all() == "ABcd1234"
    btds.close()
