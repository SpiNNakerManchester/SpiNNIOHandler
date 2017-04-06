from spinn_storage_handlers.buffered_bytearray_data_storage \
    import BufferedBytearrayDataStorage


testdata = bytearray("ABcd1234")


def test_readwrite_bytearray_buffer():
    bbds = BufferedBytearrayDataStorage()

    assert bbds is not None

    bbds.write(testdata)

    assert bbds.read_all() == testdata

    bbds.close()