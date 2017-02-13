# -*- coding: utf-8 -*-
# minix est little endian par defaut
from constantes import *
from bloc_device import *
import struct

class minix_inode(object):
    # inodes can be initializted from given values or
    # from raw bytes contents coming from the device
    def __init__(self, raw_inode=None, num=0, mode=0, uid=0, size=0, time=0, gid=0, nlinks=0, zone=[], indir_zone=0, dblr_indir_zone=0):

        if raw_inode is None:
            self.i_ino = num
            self.i_mode = mode
            self.i_uid = uid
            self.i_size = size
            self.i_time = time
            self.i_gid = gid
            self.i_nlinks = nlinks
            self.i_zone = zone
            self.i_indir_zone = indir_zone
            self.i_dbl_indr_zone = dblr_indir_zone

        #Structure of inode construction
        else:
            data = struct.unpack('<2H2I2B9H', raw_inode)
            self.i_ino = num
            self.i_mode = data[0]
            self.i_uid = data[1]
            self.i_size = data[2]
            self.i_time = data[3]
            self.i_gid = data[4]
            self.i_nlinks = data[5]
            self.i_zone = list(data[6:13])
            self.i_indir_zone = data[13]
            self.i_dbl_indr_zone = data[14]

    def __eq__(self, other):
        if isinstance(other, minix_inode):
            return self.i_ino == other.i_ino and \
                self.i_mode == other.i_mode and \
                self.i_uid == other.i_uid and \
                self.i_size == other.i_size and \
                self.i_time == other.i_time and \
                self.i_gid == other.i_gid and \
                self.i_nlinks == other.i_nlinks and \
                self.i_zone == other.i_zone and \
                self.i_indir_zone == other.i_indir_zone and \
                self.i_dbl_indr_zone == other.i_dbl_indr_zone

    def __repr__(self): #afficher
        return "minix_inode("+"num="+str(self.i_ino) + \
            ",mode="+str(self.i_mode) + \
            ",uid="+str(self.i_uid) + \
            ",size="+str(self.i_size) + \
            ",time="+str(self.i_time) + \
            ",gid="+str(self.i_gid) + \
            ",nlinks="+str(self.i_nlinks) + \
            ",zone="+str(eval(repr(self.i_zone))) + \
            ",indir_zone="+str(self.i_indir_zone) + \
            ",dblr_indir_zone="+str(self.i_dbl_indr_zone) + \
            ")"
                                                            
#    def __inv__(self, bloc_device):
#            self.bd  = bloc_device
#            data = struct.pack('<2H2I2B10H', self.i_ino, self.i_mode, self.i_uid, self.i_size, self.i_time, self.i_gid, self.i_nlinks, self.i_zone, self.i_indir_zone, self.i_dbl_indr_zone)
#            self.bd.write_bloc(1, data)