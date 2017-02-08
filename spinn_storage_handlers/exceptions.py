class DataWriteException(Exception):
    """ An exception that indicates that there was an error writing\
        to the underlying medium

        :param message: A str message to indicate what when wrong

    """

    def __init__(self, message):
        Exception.__init__(self, message)


class DataReadException(Exception):
    """ An exception that indicates that there was an error reading\
        from the underlying medium

        :param message: A str message to indicate what when wrong
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class BufferedBytearrayOperationNotImplemented(Exception):
    """ An exception that denotes that the operation required is unavailable
        for a byteArray buffer

        :param message: A message to indicate what when wrong
    """
    def __init__(self, message):
        Exception.__init__(self, message)
