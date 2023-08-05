import ctypes as C
import sys

from mpi_pyLib import getCommunicator
from mpi_pyLib import getAnyStatus
from mpi_pyLib import mpi_init
from mpi_pyLib import mpi_comm_rank
from mpi_pyLib import mpi_comm_size
from mpi_pyLib import mpi_send
from mpi_pyLib import mpi_recv
from mpi_pyLib import mpi_finalize

def main():
    rank = C.c_int
    size = C.c_int

    MPI_COMM_WORLD = getCommunicator()
    MPI_STATUS = getAnyStatus()

    mpi_init()
    data = [17,21,31,41,51,61,71, 81, 91, 11]

    mpi_rank = mpi_comm_rank(MPI_COMM_WORLD, rank)
    mpi_size = mpi_comm_size(MPI_COMM_WORLD, size)

    #print(f"rank: {mpi_rank}, size: {mpi_size}")
    #print(f"size: {mpi_size}")

    if mpi_rank == 0:
        data = [i+2 for i in range(1, 10)]
        for node in range(1, mpi_size):
            mpi_send(data, node, 1, MPI_COMM_WORLD)

        #print("Data from processor send", rank, ": ", data)
    elif mpi_rank == 1:
        print(f"Before receiving rank: {mpi_rank}, data {data} ")
        data = mpi_recv(data, 0, 1, MPI_COMM_WORLD)

        print(f"After receiving rank: {mpi_rank}, data {data} ")
        #print(f"Data from processor recv {mpi_rank}: {data}") 

    mpi_finalize()

main()
