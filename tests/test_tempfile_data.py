# import py.test
from spinn_storage_handlers import BufferedTempfileDataStorage


testdata = bytearray("ABcd1234")
MANY_TEMP_FILES = 2000


def test_readwrite_tempfile_buffer(tmpdir):
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
        b.write(str(i))
        temps.append(b)
    vals = list()
    for t in temps:
        vals.append(int(t.read()))
    assert vals == sorted(list(vals))
    for t in temps:
        t.close()
