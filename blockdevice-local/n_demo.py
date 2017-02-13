#! /usr/bin/env python2

from constantes import *


def isdir(inode):
	return inode.i_mode & 0x4


def listdir(fs, path):
	inode = fs.inodes_list[fs.namei(path)]

	if not isdir(inode):
		return

	for block in xrange(0, MINIX_ZONESZ ** 2 + MINIX_ZONESZ + 7):
		data_block = fs.bmap(inode, block)

		if data_block == 0:
			break

		data = bytearray(fs.disk.read_bloc(data_block))

		for offset in xrange(0, BLOCK_SIZE, DIRSIZE):
			if data[offset:offset+2] != '\0\0':
				print data[offset+2:offset+16].strip('\0')

def mkdir(fs, path, name):
	parent = fs.inodes_list[fs.namei(path)]

	if not isdir(parent):
		return

	inode_id = fs.ialloc()
	inode = fs.inodes_list[inode_id]
	inode.i_mode = 0x4  # folder mask
	inode.i_zone = [0] * 7

	fs.add_entry(parent, name, inode_id)

def rmdir(fs, path, name):
	parent = fs.inodes_list[fs.namei(path)]

	if not isdir(parent):
		return

	inode = fs.inodes_list[fs.namei(path + '/' + name)]


	for block in xrange(0, MINIX_ZONESZ ** 2 + MINIX_ZONESZ + 7):
		data_block = fs.bmap(inode, block)

		if data_block == 0:
			break

		fs.bfree(data_block)

	fs.del_entry(parent, name)
	fs.ifree(inode.i_ino)



def main():
    pass

if __name__ == '__main__':
    main()