import ctypes as C
import numpy as np
import sys

from mpi_pyLib import getCommunicator
from mpi_pyLib import getAnyStatus
from mpi_pyLib import mpi_init
from mpi_pyLib import mpi_comm_rank
from mpi_pyLib import mpi_comm_size
from mpi_pyLib import mpi_send
from mpi_pyLib import mpi_recv
from mpi_pyLib import mpi_finalize
from mpi_pyLib import mpi_bcast


MASTER = 0

def main():

    MPI_COMM_WORLD = getCommunicator()
    MPI_STATUS = getAnyStatus()

    RANK = C.c_int
    SIZE = C.c_int

    mpi_init()
    #data = list()
    RANK = mpi_comm_rank(MPI_COMM_WORLD, RANK)
    SIZE = mpi_comm_size(MPI_COMM_WORLD, SIZE)


    if RANK == MASTER:
        data = [1.5, 2.9, 30.9, 9.9]
    else:
        data = []

    data = mpi_bcast(data, MASTER, 0, MPI_COMM_WORLD)
    print(f"rank: {RANK} \t{data}")

    mpi_finalize()

if __name__ == "__main__":
    main()
