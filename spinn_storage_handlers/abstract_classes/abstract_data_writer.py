from six import add_metaclass
from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractDataWriter(object):
    """ Abstract writer used to write data somewhere.
    """

    __slots__ = []

    @abstractmethod
    def write(self, data):
        """ Write some bytes of data to the underlying storage.\
            Does not return until all the bytes have been written.

        :param data: The data to write
        :type data: bytearray or bytes
        :return: Nothing is returned
        :rtype: None
        :raise IOError: If an error occurs writing to the underlying storage
        """

    @abstractmethod
    def tell(self):
        """ Returns the position of the file cursor.

        :return: Position of the file cursor
        :rtype: int
        """
