# import py.test
from spinn_storage_handlers import BufferedTempfileDataStorage
import os


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
        assert b not in temps
        temps.append(b)
        s = str(i)
        assert len(s) > 0
        b.write(bytearray(s))
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
