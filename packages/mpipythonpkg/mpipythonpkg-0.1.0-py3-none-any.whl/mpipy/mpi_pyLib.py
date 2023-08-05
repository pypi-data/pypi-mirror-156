import ctypes as C

class MPI_Status(C.Structure):
    _fields_ = [("count_lo", C.c_int),
                ("count_hi_and_cancelled", C.c_int),
                ("MPI_SOURCE", C.c_int),
                ("MPI_TAG", C.c_int),
                ("MPI_ERROR", C.c_int)]

"""Load my library."""
_c_pylib = C.CDLL("./c_pylib.so")


_c_pylib.getCommunicator.restype = C.c_int
_c_pylib.getAnyStatus.restype = C.POINTER(MPI_Status)
_c_pylib.mpi_send.argtypes = (C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_int)
_c_pylib.mpi_recv.argtypes = (C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_int)


"""
Wrapping for pure MPI.
"""

_c_pylib.MPI_Init.argtypes = (C.POINTER(C.c_int), C.POINTER(C.POINTER(C.POINTER(C.c_char))))
_c_pylib.MPI_Comm_rank.argtypes = (C.c_int, C.POINTER(C.c_int))
_c_pylib.MPI_Comm_size.argtypes = (C.c_int, C.POINTER(C.c_int))
_c_pylib.MPI_Send.argtypes = (C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_int, C.c_int)
_c_pylib.MPI_Recv.argtypes = (C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_int, C.c_int, C.POINTER(MPI_Status))

_c_pylib.MPI_Init.restype = C.c_int
_c_pylib.MPI_Comm_rank.restype = C.c_int
_c_pylib.MPI_Comm_size.restype = C.c_int
_c_pylib.MPI_Send.restype = C.c_int
_c_pylib.MPI_Recv.restype = C.c_int
_c_pylib.MPI_Finalize.restype = C.c_int


def getCommunicator():
    global _c_pylib
    return _c_pylib.getCommunicator()

def getAnyStatus():
    global _c_pylib
    return _c_pylib.getAnyStatus()

def mpi_init():
    global _c_pylib
    _c_pylib.MPI_Init(None, None)

def mpi_comm_size(COMM, SIZE):
    global _c_pylib
    SIZE = C.c_int()
    _c_pylib.MPI_Comm_size(COMM, SIZE)
    return SIZE.value

def mpi_comm_rank(COMM, RANK):
    global _c_pylib
    RANK = C.c_int()
    _c_pylib.MPI_Comm_rank(COMM, RANK)
    return RANK.value

def mpi_finalize():
    global _c_pylib
    _c_pylib.MPI_Finalize()

def mpi_send(data, destination, tag, COMM):
    global _c_pylib

    parsedData = (C.c_double * len(data))(*data)

    """
    Encode string into byte object.
    Then, convert it into string buffer that can be decayed into
    char pointer.
    """
    #parsedData = data.encode("utf-8")
    #parsedData = C.create_string_buffer(parsedData)

    _c_pylib.mpi_send(parsedData, len(data), destination, tag, COMM)

def mpi_recv(data, source, tag, COMM):
    global _c_pylib
    parsedData = (C.c_double * len(data))(*data)

    """
    Encode string into byte object.
    Then, convert it into string buffer that can be decayed into
    char pointer.
    """
    #parsedData = data.encode("utf-8")
    #parsedData = C.create_string_buffer(parsedData)

    _c_pylib.mpi_recv(parsedData, len(data), source, tag, COMM)

    parsedData = [parsedData[i] for i in range(len(data))]
    return parsedData




def mpi_bcast(data, count, source, COMM):
    global _c_pylib

    parsedData = (C.c_double * len(data))(*data)

    _c_pylib.mpi_bcast(parsedData, len(data), source, COMM)

    parsedData = [parsedData[i] for i in range(len(data))]
    return parsedData

