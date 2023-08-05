"""
Developer: Elkana Munganga


"""

import ctypes as C
import sys
from mpi_pyLib import getCommunicator, getAnyStatus,\
        mpi_init, mpi_comm_rank, mpi_comm_size,\
        mpi_send, mpi_recv, mpi_finalize



def main():

    MPI_COMM_WORLD = getCommunicator()
    MPI_STATUS = getAnyStatus()
    
    size = C.c_int
    rank = C.c_int

    mpi_init()

    mpi_rank = mpi_comm_rank(MPI_COMM_WORLD, rank)
    mpi_size = mpi_comm_size(MPI_COMM_WORLD, size)
    
    if (mpi_rank == 0):
        data = [float(i) for i in range(1, 10)]
    elif (mpi_rank != 0):
        data = [float(0) for i in range(1, 10)]
        print("Initial data at rank {}: {}".format(mpi_rank, data))

    if (mpi_rank == 0):
    
        for node in range(1, mpi_size):
            mpi_send(data, node, 1, MPI_COMM_WORLD)

    elif (mpi_rank == 1):
        
        data = mpi_recv(data, 0, 1, MPI_COMM_WORLD)
        print("data received at rank {}: {}".format(mpi_rank, data))


    mpi_finalize()

if __name__ == "__main__":
    main()
