class DataWriteException(Exception):
    """ An exception that indicates that there was an error writing\
        to the underlying medium
    """


class DataReadException(Exception):
    """ An exception that indicates that there was an error reading\
        from the underlying medium
    """


class BufferedBytearrayOperationNotImplemented(NotImplementedError):
    """ An exception that denotes that the operation required is unavailable\
        for a byteArray buffer
    """
