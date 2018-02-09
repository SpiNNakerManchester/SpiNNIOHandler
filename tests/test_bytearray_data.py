from spinn_storage_handlers import BufferedBytearrayDataStorage
from spinn_storage_handlers.exceptions \
    import DataWriteException, BufferedBytearrayOperationNotImplemented
import pytest
import os

testdata = bytearray("ABcd1234")


def test_readwrite_bytearray_buffer():
    bbds = BufferedBytearrayDataStorage()
    assert bbds is not None
    bbds.write(testdata)
    assert bbds.read_all() == testdata
    with pytest.raises(BufferedBytearrayOperationNotImplemented):
        bbds.readinto(bytearray(123))
    bbds.close()


def test_basic_ops():
    with BufferedBytearrayDataStorage() as buf:
        assert buf.tell_read() == 0
        assert buf.tell_write() == 0
        assert buf.eof() is True

        assert buf.read(123) == ''

        buf.write(bytearray('abc'))
        with pytest.raises(DataWriteException):
            buf.write('def')
        assert buf.tell_write() == 3
        assert buf.tell_read() == 0
        assert buf.eof() is False

        assert buf.read(1) == 'a'
        assert buf.tell_read() == 1
        assert buf.tell_write() == 3

        assert buf.read(5) == 'bc'
        assert buf.tell_read() == 3
        assert buf.eof() is True

        buf.seek_read(2)
        assert buf.read(5) == 'c'
        assert buf.eof() is True
        buf.write(bytearray('def'))
        assert buf.eof() is False
        buf.seek_read(2)
        assert buf.read(5) == 'cdef'
        assert buf.eof() is True

        buf.seek_write(2)
        buf.write(bytearray('PQR'))
        buf.seek_read(0)
        assert buf.read(4) == 'abPQ'
        assert buf.eof() is False

        buf.seek_write(6)
        buf.write(bytearray("gh"))
        buf.seek_read(1, os.SEEK_SET)
        assert buf.read(1) == 'b'
        buf.seek_read(1, os.SEEK_CUR)
        assert buf.read(1) == 'Q'
        buf.seek_read(-2, os.SEEK_END)
        assert buf.read(1) == 'g'
