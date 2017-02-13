# -*- coding: utf-8 -*-
from constantes import *
from bloc_device import *
from struct import *
from math import *

#ici je recois un objet bloc device. 
# lire de block 1 
# avec struct parser
# ici le superbloc va me dire combien de inodes j'ai
# regarder lib python STRUCT. unpack()
class minix_superbloc(object):
    def __init__(self, bloc_device):

        #Declaration constantes.
        superblock = bloc_device.read_bloc(1)[0:20]
        data = struct.unpack('<HHHHHHIHH', superblock)
        
        self.s_ninodes = data[0]
        self.s_nzones = data[1]
        self.s_imap_blocks = data[2]
        self.s_zmap_blocks = data[3]
        self.s_firstdatazone = data[4]
        self.s_log_zone_size = data[5]
        self.s_max_size = data[6]
        self.s_magic = data[7]
        self.s_state = data[8]
