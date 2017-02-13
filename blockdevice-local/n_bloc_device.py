# -*- coding: utf-8 -*-
# emulate a simple bloc device using a file
# reading it only by bloc units
from sys import *
from constantes import *
from math import ceil
from string import *

class bloc_device(object):
    def __init__(self, blksize, pathname):
        #Stock in the structure the pathname and the blksize 1024 by default
        self.pathname = pathname
        self.file_bloc = open(pathname, 'rb+') # read + binary
        self.blksize = BLOCK_SIZE
        self.file_bloc.seek(0) #start of file_bloc
        #print (self.blksize)

    def read_bloc(self, bloc_num, numofblk=1) :
        #TO CORRECT
        # Check if we are correctly reading the bloc.
        if bloc_num < 0:
            raise IndexError('bloc_num out of bounds')

        #Read the block and return array of bytes
        self.file_bloc.seek(self.blksize * bloc_num)
        return self.file_bloc.read(BLOCK_SIZE * numofblk)

    def write_bloc(self, bloc_num, bloc): #bloc = ma chaine de char
        if (bloc_num < 0) :
            return 0
        else:
            self.file_bloc.seek(BLOCK_SIZE * bloc_num)
            buff = buffer(bloc, 0, BLOCK_SIZE)
            for i in range(BLOCK_SIZE):
                self.file_bloc.write(buff[i])
            self.file_bloc.flush()
        return
