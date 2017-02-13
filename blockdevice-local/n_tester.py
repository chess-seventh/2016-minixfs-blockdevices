# -*- coding: utf-8 -*-
# filesystem and bloc device unit tests
# part 1: internal filesystem's functions.
# tested with python2 only

from constantes import *
from bloc_device import *
from minixfs import *
from bitarray import *
from tester_answers import *
import unittest
import os
import sys

# Test requirements : 
# - bloc_device class : modeling a disk drive with the following methods
#   -  read_bloc, write_bloc
# - minix_superbloc class : a structure storing minix superblocs infos.
# - minix_inode class : a structure modeling a minix inode
# - minix_filesystem class : modeling minix filesystem class with the following methods:
#   - ialloc(), ifree(), balloc(), bfree()
#   - bmap(), lookup_entry(), namei()
#   - ialloc_bloc(), add_entry(), del_entry()
# - bitarray class : used to store and manipulated inode and zone bitmaps in memory
#   member ofs minix_filesystem class

testfile="minixfs_lab1.img"
workfile=testfile+".gen"
workfilewrite=testfile+".genwrite"
string="dd if="+testfile+" of="+workfile+" bs=1024 2>/dev/null"
os.system(string)

class MinixTester(unittest.TestCase):

    #test if the content returned by read_bloc 
    #is the one we expect.
    def test_1_bloc_device_read_bloc(self):
        self.disk=bloc_device(BLOCK_SIZE,workfile)
        bloc2=self.disk.read_bloc(2)
        bloc5=self.disk.read_bloc(5)
        bloc7=self.disk.read_bloc(7)
        bloc24=self.disk.read_bloc(24)
        self.assertEqual(bloc2,BLOC2)
        self.assertEqual(bloc5,BLOC5)
        self.assertEqual(bloc7,BLOC7)
        self.assertEqual(bloc24,BLOC24)
    
    #exchange bloc2 and bloc5 on the bloc device and test if the content 
    #returned by read_bloc on it matches.
    def test_2_bloc_device_write_bloc(self):
        string="dd if="+workfile+" of="+workfilewrite+" bs=1024 2>/dev/null"
        os.system(string)
        self.disk=bloc_device(BLOCK_SIZE,workfilewrite)
        #read bloc2 and bloc5
        bloc2=self.disk.read_bloc(2)
        bloc5=self.disk.read_bloc(5)
        #swap them
        tmp=bloc2
        bloc2=bloc5
        bloc5=tmp
        #write them
        self.disk.write_bloc(2,bloc2)
        self.disk.write_bloc(5,bloc5)
        #check if they are effectively swapped
        bloc2=self.disk.read_bloc(2)
        bloc5=self.disk.read_bloc(5)
        self.assertEqual(bloc2,BLOC5)
        self.assertEqual(bloc5,BLOC2)

    #superbloc test : read it and check object values
    def test_3_super_bloc_read_super(self):
        self.disk=bloc_device(BLOCK_SIZE,workfile)
        sb=minix_superbloc(self.disk)
        
        self.assertEqual(sb.s_ninodes,6848)
        self.assertEqual(sb.s_nzones,20480)
        self.assertEqual(sb.s_imap_blocks,1)
        self.assertEqual(sb.s_zmap_blocks,3)
        self.assertEqual(sb.s_firstdatazone,220)
        self.assertEqual(sb.s_max_size,268966912)

    #inode and zone map tests
    #we need to copy the original as it was modified 
    #when testing write_bloc
    def test_4_fs_inode_and_bloc_bitmaps(self):
        self.minixfs=minix_file_system(workfile)
        self.assertEqual(self.minixfs.inode_map,INODEBITMAP1);
        self.assertEqual(self.minixfs.zone_map,ZONEBITMAP1);

    #inode list content test
    def test_5_fs_inode_list(self):
        self.minixfs=minix_file_system(workfile)
        self.assertEqual(self.minixfs.inodes_list,INODELIST);


    #testing ialloc()/ifree()
    #calling ialloc()/ifree() several time and checking
    #the bitmask values after/or checking the number returned
    #by ialloc after ifree and balloc after bfree.
    def test_6_fs_ialloc_ifree(self):
        self.minixfs=minix_file_system(workfile)
        new_inode_num=self.minixfs.ialloc()
        self.assertEqual(new_inode_num,NEWNODE1);
        self.minixfs.ifree(123)
        new_inode_num=self.minixfs.ialloc()
        self.assertEqual(new_inode_num,NEWNODE2);
        new_inode_num=self.minixfs.ialloc()
        self.assertEqual(new_inode_num,NEWNODE3);

    #testing balloc()/bfree()
    #same method as ialloc/ifree testing
    #balloc write on the filesystem as it initialize all bloc bytes to \0
    def test_7_fs_balloc_bfree(self):
        string="dd if="+workfile+" of="+workfilewrite+" bs=1024 2>/dev/null"
        os.system(string)
        self.minixfs=minix_file_system(workfilewrite)
        new_bloc_num=self.minixfs.balloc()
        self.assertEqual(new_bloc_num,NEWBLOC1);
        self.minixfs.bfree(123)
        new_bloc_num=self.minixfs.balloc()
        self.assertEqual(new_bloc_num,NEWBLOC2);
        new_bloc_num=self.minixfs.balloc()
        self.assertEqual(new_bloc_num,NEWBLOC3);
        return True

    #testing bmap function : just check that some bmaped
    #blocs have the right numbers.
    def test_8_fs_bmap(self):
        minixfs=minix_file_system(workfile)
        #bmap of inode 167, an inode with triple indirects 
        #containing linux-0.95.tgz. Get all blocs of the file
        #direct blocs
        dir_bmap_list=[]
        for i in range(0,7):
            bmap_bloc=minixfs.bmap(minixfs.inodes_list[167],i)
            dir_bmap_list.append(bmap_bloc)
        self.assertEqual(dir_bmap_list,DIRMAP)
        
        #indirect blocs
        indir_bmap_list=[]
        for i in range(7,512+7):
            bmap_bloc=minixfs.bmap(minixfs.inodes_list[167],i)
            indir_bmap_list.append(bmap_bloc)
        self.assertEqual(indir_bmap_list,INDIRMAP)
        
        #double indirect blocs
        dbl_indir_bmap_list=[]
        for i in range(512+7,1024):
            bmap_bloc=minixfs.bmap(minixfs.inodes_list[167],i)
            dbl_indir_bmap_list.append(bmap_bloc)
        self.assertEqual(dbl_indir_bmap_list,DBLINDIRMAP)

    #testing lookup_entry function : give a known inode 
    #number, and name, expect another inode number
    #do a few lookups
    def test_9_fs_lookup_entry(self):
        minixfs=minix_file_system(workfile)
        #lookup_entry, inode 798 ("/usr/src/ps-0.97"), lookup for ps.c 
        inode=minixfs.lookup_entry(minixfs.inodes_list[798],"ps.c")
        self.assertEqual(inode,LOOKUPINODE1)
        #lookup_entry, inode 212 ("/usr/src/linux/fs/minix"), lookup for namei.c 
        inode=minixfs.lookup_entry(minixfs.inodes_list[212],"namei.c")
        self.assertEqual(inode,LOOKUPINODE2)


    #testing namei function. Test that a few paths return
    #the expected inode number.
    def test_a_fs_namei(self):
        minixfs=minix_file_system(workfile)
        paths=["/usr/src/linux/fs/open.c","/bin/bash","/","/usr/include/assert.h"]
        namedinodelist=[]
        for p in paths:
            namedinode=minixfs.namei(p)
            namedinodelist.append(namedinode)
        self.assertEqual(namedinodelist,NAMEDINODES)

    #testing i_add_bloc, i_alloc_bloc ? 
    #function allocate a new bloc for a given file in the bloc list.
    #check its bloc list in the inode, before and after addition
    #check that bmap on the inode return the newly added bloc number
    #do one direct i_alloc and one indirect i_alloc.
    #we might need to get a fresh copy of the filesystem
    def test_b_fs_ialloc_bloc(self):
        string="dd if="+workfile+" of="+workfilewrite+" bs=1024 2>/dev/null"
        os.system(string)
        minixfs=minix_file_system(workfilewrite)
        dir_bmap_list=[]
        for i in range(0,7):
            bmap_bloc=minixfs.bmap(minixfs.inodes_list[56],i)
            dir_bmap_list.append(bmap_bloc)
        self.assertEqual(dir_bmap_list,IALLOC1)
    
        #ialloc bloc 2 and 3 on the inode
        bmap_bloc=minixfs.ialloc_bloc(minixfs.inodes_list[56],2)
        bmap_bloc=minixfs.ialloc_bloc(minixfs.inodes_list[56],3)
        #print bmap again
        dir_bmap_list=[]
        for i in range(0,7):
            bmap_bloc=minixfs.bmap(minixfs.inodes_list[56],i)
            dir_bmap_list.append(bmap_bloc)
        self.assertEqual(dir_bmap_list,IALLOC2)

    #testing bloc contents and inode maps before and after add_entry
    def test_c_fs_addentry(self):
        string="dd if="+workfile+" of="+workfilewrite+" bs=1024 2>/dev/null"
        os.system(string)
        minixfs=minix_file_system(workfilewrite)
        self.assertEqual(minixfs.bmap(minixfs.inodes_list[1],0),ROOTNODEBLOCNUM1)
        
        rootnodebloc=minixfs.disk.read_bloc(minixfs.bmap(minixfs.inodes_list[1],0))
        self.assertEqual(rootnodebloc,ROOTNODEBLOC1)
        for i in range(1,57):
            minixfs.add_entry(minixfs.inodes_list[1],"new_ent"+str(i),minixfs.ialloc())
    
        rootnodebloc=minixfs.disk.read_bloc(minixfs.bmap(minixfs.inodes_list[1],0))
        self.assertEqual(rootnodebloc,ROOTNODEBLOC1MOD)
        
        #more complex modification : add enough entries so that a new bloc must be allocated
        #check that the next bloc is still 0
        self.assertEqual(minixfs.bmap(minixfs.inodes_list[1],1),ROOTNODEBLOCNUM2)
        #add some more entries
        for i in range(57,60):
            minixfs.add_entry(minixfs.inodes_list[1],"new_ent"+str(i),minixfs.ialloc())
        #check that new bloc has been allocated
        self.assertEqual(minixfs.bmap(minixfs.inodes_list[1],1),ROOTNODEBLOCNUM2NEW)
        #check its contents
        rootnodebloc2=minixfs.disk.read_bloc(minixfs.bmap(minixfs.inodes_list[1],1))
        self.assertEqual(rootnodebloc2,ROOTNODEBLOC2MOD)
    
    #testing bloc contents and inode maps before and after del_entry
    def test_d_fs_delentry(self):
        NODENUM=798
        names_to_del=["attime.c","cmdline.c","free","free.c","Makefile","makelog","ps","ps.0","ps.1","ps.c","psdata.c","psdata.h","ps.h","pwcache.c"]
        string="dd if="+workfile+" of="+workfilewrite+" bs=1024 2>/dev/null"
        os.system(string)
        minixfs=minix_file_system(workfilewrite)
        self.assertEqual(minixfs.bmap(minixfs.inodes_list[NODENUM],0),NODE798BLOCNUM1)
    
        nodebloc=minixfs.disk.read_bloc(minixfs.bmap(minixfs.inodes_list[NODENUM],0))
        self.assertEqual(nodebloc,NODE798BLOC1)

        for name in names_to_del:
            minixfs.del_entry(minixfs.inodes_list[NODENUM],name)
        nodebloc=minixfs.disk.read_bloc(minixfs.bmap(minixfs.inodes_list[NODENUM],0))
        self.assertEqual(nodebloc,NODE798BLOC1MOD)

    def test_e_cleanup(self):
        #clean up
        os.system("rm *.pyc")
        os.system("rm "+workfile+" "+workfilewrite)
        return True


if __name__ == '__main__' :
    unittest.main()
