from enum import Enum


class Mode(Enum):
    """
    Mode of the socket.
    """
    SERVER = 0
    CLIENT = 1

class Protocol(Enum):
    """
    Protocol of the socket.
    """
    TCP = 0
    UDP = 1