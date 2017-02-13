# -*- coding: utf-8 -*-
# Note : minix-fs types are little endian

from constantes import *
from minix_inode import *
from minix_superbloc import *
from bloc_device import *
from array import *
from math import ceil
from string import *

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

class minix_file_system(object):
    def __init__(self, filename):
        self.disk = bloc_device(BLOCK_SIZE, filename)
        self.superBloc = minix_superbloc(self.disk)

        self.bitmap_inode_offset = 2
        self.bitmap_bloc_offset = self.superBloc.s_imap_blocks + 2
        self.inode_offset = self.bitmap_bloc_offset + self.superBloc.s_zmap_blocks
        self.bloc_offset = self.superBloc.s_firstdatazone

        self.empty_bloc = BLOCK_SIZE * '\0'

        raw_inode_map = self.disk.read_bloc(2, self.superBloc.s_imap_blocks)
        self.inode_map = bitarray(endian='little')
        self.inode_map.frombytes(raw_inode_map)

        #data bitmap
        raw_zone_map = self.disk.read_bloc(self.bitmap_bloc_offset, self.superBloc.s_zmap_blocks)
        self.zone_map = bitarray(endian='little')
        self.zone_map.frombytes(raw_zone_map)

        self.inodes_list = []
        self.inodes_list.append(minix_inode(None))
        nb_inodes = self.superBloc.s_ninodes
        nb_blocs_inodes = int(ceil(nb_inodes * INODE_SIZE / BLOCK_SIZE))
        

        raw_inodes = self.disk.read_bloc(self.inode_offset, nb_blocs_inodes)

        for i, chunk in enumerate(chunks(raw_inodes, INODE_SIZE)):
            self.inodes_list.append(minix_inode(chunk, i + 1))



    # return the first free inode number available
    # starting at 0 and upto s.n_inodes-1.
    # The bitmap ranges from index 0 to inod_num-1
    # Inode 0 is never used and is always set.
    # according to the inodes bitmap
    def ialloc(self):
        first_free_inode = self.inode_map.index(False)
        if first_free_inode == 0:
            return False
        self.inode_map[first_free_inode] = True
        self.inodes_list.pop(first_free_inode)
        self.inodes_list.insert(first_free_inode, minix_inode())
        return int(first_free_inode)





    # toggle an inode as available for the next ialloc()
    def ifree(self, inodnum):
        self.inode_map[inodnum] = False
        return




    # return the first free bloc index in the volume. The bitmap
    # indicate the index from the bloc zone, add first_datazone then
    # to the bloc index
    def balloc(self):
        free_data_index = self.zone_map.index(False)
        self.zone_map[free_data_index] = True
        num_bloc_towrite = self.bloc_offset + free_data_index
        self.disk.write_bloc(num_bloc_towrite, self.empty_bloc) #on ecrit tout a 0 du bloc
        return int(free_data_index + self.bloc_offset)




    # toggle a bloc as available for the next balloc()
    # blocnum is an index in the zone_map
    def bfree(self, blocnum):
        self.zone_map[blocnum] = False
        return




    # function BMAP:
    def bmap(self, inode, blk):

        #cas pas d'indirection
        if blk < 7:
            return inode.i_zone[blk]

        # relativisation
        blk -= 7

        # cas simple indirection 
        if blk < MINIX_ZONESZ:
            bloc_indirect = self.disk.read_bloc(inode.i_indir_zone)
            offset = blk * (BLOCK_SIZE / MINIX_ZONESZ)
            return struct.unpack_from('<H', bloc_indirect, offset)[0]

        #relativisation
        blk -= MINIX_ZONESZ

        if blk < (MINIX_ZONESZ * MINIX_ZONESZ):
            # cas double indirection

            bloc_indirect_1 = self.disk.read_bloc(inode.i_dbl_indr_zone)
            offset_1 = blk*(BLOCK_SIZE/(MINIX_ZONESZ*MINIX_ZONESZ))
            
            address_indirect_2 = struct.unpack_from('<H', bloc_indirect_1, offset_1)[0]
            bloc_indirect_2 = self.disk.read_bloc(address_indirect_2)

            offset_2 = ((blk % MINIX_ZONESZ) * (BLOCK_SIZE / MINIX_ZONESZ))

            return struct.unpack_from('<H', bloc_indirect_2, offset_2)[0]




    # lookup for a name in a directory, and return its inode number,
    # given inode directory dinode
    def lookup_entry(self, dinode, name):
        for i in range(0, dinode.i_size):
            bloc_id = self.bmap(dinode, i)

            if bloc_id == 0:
                break

            bloc = self.disk.read_bloc(bloc_id)
            for j in range(0, MINIX_INODE_PER_BLOCK):
                inode = bloc[INODE_SIZE * j : INODE_SIZE * (j + 1)]
                if name in inode[2:16]:
                    return struct.unpack('<H', inode[0:2])[0]
        return 0



    # find an inode number according to its path
    # ex : '/usr/bin/cat'
    # only works with absoluteTwo module-level constants are defined for the f_flag attribute’s bit-flags: if ST_RDONLY is set, the filesystem is mounted read-only, and if ST_NOSUID is set, the semantics of setuid/setgid bits are disabled or not supported. paths
    def namei(self, path):
        inode = MINIX_ROOT_INO
        if path == '/':
            return inode
        for i in path[1:len(path)].split('/'):
            inode = self.lookup_entry(self.inodes_list[inode], i)
        return inode




    # parameters : inode number , blk number
    # return the block number allocated
    def ialloc_bloc(self, inode, blk):
        # 2 cas a traiter
        #cas 0
        if (blk < len(inode.i_zone)):
            if (inode.i_zone[blk] == 0):
                inode.i_zone[blk] = self.balloc()
                inode.i_size += BLOCK_SIZE
            return inode.i_zone[blk]

        #relativisation
        blk -= len(inode.i_zone)

        if (blk < 512):
            if (inode.i_indir_zone == 0):
                inode.i_indir_zone = self.balloc()

            indirect_bloc = self.disk.read_bloc(inode.i_indir_zone)
            indirect_bloc = list(struct.unpack('<512H', indirect_bloc))
            #addr = indirect_bloc[blk]

            if (indirect_bloc[blk] == 0):
                indirect_bloc[blk] = self.balloc()
                indirect_bloc = struct.pack('<512H', indirect_bloc)
                indirect_bloc = self.balloc()
                self.disk.write_bloc(inode.i_indir_zone, indirect_bloc)
                inode.i_size += BLOCK_SIZE
                
            return indirect_bloc[blk]
        
        return 0


    
    # create a new entry in the node
    # name is an unicode string
    # parameters : directory inode, name, inode number
    def add_entry(self, dinode, name, new_node_num):
        
        for blk_id in range(0, int(ceil(dinode.i_size / BLOCK_SIZE))+ 1):
            if blk_id > MINIX_ZONESZ ** 2 + MINIX_ZONESZ + 7:
                raise IndexError('Out of bounds') 

            addr = self.ialloc_bloc(dinode, blk_id)  # works as bmap when block is already allocated

            data_blk = bytearray(self.disk.read_bloc(addr))

            for dir_off in xrange(0, BLOCK_SIZE, DIRSIZE):
                if struct.unpack_from('<H', data_blk, dir_off)[0] == 0:
                    struct.pack_into('<H 14s', data_blk, dir_off, new_node_num, name[:14])
                    self.disk.write_bloc(addr, data_blk)
                    dinode.i_size += DIRSIZE
                    return     
        

    # delete an entry named "name"
    def del_entry(self, inode, name):
        for blk_id in range(0, MINIX_ZONESZ ** 2 + MINIX_ZONESZ + 7):               
            addr = self.bmap(inode, blk_id)

            if addr == 0:
                return  # no more blocks

            data_blk = bytearray(self.disk.read_bloc(addr))

            for dir_off in xrange(0, BLOCK_SIZE, DIRSIZE):
                entry_name = str(data_blk[dir_off+2:dir_off+16].strip('\0'))

                if entry_name == name:
                    struct.pack_into('<H', data_blk, dir_off, 0)
                    self.disk.write_bloc(addr, data_blk)
                    inode.i_size -= DIRSIZE
                    return  # found and removed
        
