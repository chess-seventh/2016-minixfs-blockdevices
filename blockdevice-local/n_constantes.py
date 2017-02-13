# -*- coding: utf-8 -*-
import sys
import struct
import os
import time
from stat import *
from bitarray import *

# block size in bytes
BLOCK_SIZE = 1024
# on which block number is the superbloc
MINIX_SUPER_BLOCK_NUM = 1
# that's in octets units
MINIX_SUPER_BLOCK_SIZE = 20
MINIX_ROOT_INO = 1
# zone number are encoded with 2 bytes
# hence 512 possible indirect zones in a bloc
MINIX_ZONESZ = int(BLOCK_SIZE/2)
DIRSIZE = 16
MAXOPENFILE = 10
MINIX_DIR_ENTRIES_PER_BLOCK = BLOCK_SIZE/DIRSIZE
# inode types
I_DIRECTORY = 0o040000
I_REGULAR = 0o100000
# inode structure size in bytes
INODE_SIZE = 32
MINIX_INODE_PER_BLOCK = BLOCK_SIZE/INODE_SIZE
