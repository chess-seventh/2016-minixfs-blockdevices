# -*- coding: utf-8 -*-
"""
Emulate a simple block device using the block server reading and wirintg on it
only by blocks.
"""
import time
import random
import socket
import struct

from os import strerror


CMD_READ = 0x0
CMD_WRITE = 0x1


def recv_exact(self, buffersize):
    """
    Receive the exact specified number of bytes.
    """
    remaining = buffersize
    buf = ''

    while remaining > 0:
        data = self.recv(remaining)
        buf += data
        remaining -= len(data)

    return buf
socket.socket.recv_exact = recv_exact  # monkey patching


class Request(object):
    """
    Request representation.
    """

    _MAGIC = '\x76\x76\x76\x76'
    _FMT = '!4i'

    def __init__(self, offset, length=None, payload=None, handle=None):
        self._handle = handle or random.getrandbits(31)
        self._offset = offset

        self._payload = payload
        self._length = length
        self._cmd = CMD_READ

        if payload is not None:
            if length is not None:
                raise ValueError("length and payload are mutualy exclusive")
            self._length = len(payload)
            self._cmd = CMD_WRITE
        elif length is None:
            raise ValueError("length or payload must be specified")

    def to_bytes(self):
        """
        Pack the request as a network packet.
        """
        header = struct.pack(
            self._FMT,
            self._cmd,
            self._handle,
            self._offset,
            self._length,
        )
        payload = self._payload or ''

        return self._MAGIC + header + payload

    def to_socket(self, sock):
        """
        Send the request over the specified socket.
        """
        sock.sendall(self.to_bytes())

    @property
    def handle(self):
        """
        Read-only request's handle.
        """
        return self._handle

    @property
    def length(self):
        """
        Read-only request's length.
        """
        return self._length

    @property
    def cmd(self):
        """
        Read-only request's command.
        """
        return self._cmd


class Response(object):
    """
    Response representation.
    """

    _MAGIC = '\x87\x87\x87\x87'
    _FMT = '!2i'
    _HEADER_SIZE = 12  # magic 4 bytes + handle 4 bytes + error 4 bytes
    _HEADER_PART = _HEADER_SIZE - 3

    @classmethod
    def from_bytes(cls, header, payload=None):
        """
        Unpack a response from splited header and payload network data.
        """
        header = struct.unpack(cls._FMT, header)
        return Response(handle=header[1], error=header[0], payload=payload)

    @classmethod
    def from_socket(cls, request, sock):
        """
        Unpack the response related to the specified request from the given
        socket.
        """
        buf = sock.recv_exact(cls._HEADER_SIZE)

        offset = buf.find(cls._MAGIC)

        while offset == -1:
            # truncate and complete
            buf = buf[cls._HEADER_PART:] + sock.recv_exact(cls._HEADER_PART)
            offset = buf.find(cls._MAGIC)

        buf = buf[offset:]
        if len(buf) < cls._HEADER_SIZE:
            buf += sock.recv_exact(cls._HEADER_SIZE - len(buf))

        header = buf[4:]  # skip magic number

        if request.cmd == CMD_READ and header[:4] == '\0\0\0\0':
            payload = sock.recv_exact(request.length)
        else:
            payload = ''

        return cls.from_bytes(header, payload)

    def __init__(self, handle, error, payload):
        self._handle = handle
        self._error = error
        self._length = len(payload)
        self._payload = payload or None

    @property
    def handle(self):
        """
        Read-only response's handle.
        """
        return self._handle

    @property
    def error(self):
        """
        Read-only response's error.
        """
        return self._error

    @property
    def payload(self):
        """
        Read-only response's payload.
        """
        return self._payload


class NetBlockDevice(object):
    """
    BlockDevice interface over tcp connection using sockets.
    """

    def __init__(self, blocksize, host, port):
        """
        Establish connection to the server and expose data by a block API.

        :arg blocksize: Block size in bytes
        :arg host: Remote server IP address (IPv4 only)
        :arg port: Tcp port used for the connection
        """
        self._blocksize = blocksize
        self._host = host
        self._port = port

        random.seed(time.time())

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def read_block(self, index, count=1):
        """
        Read block(s) from the specified index.

        :arg index: Index of the first block to read
        :arg count: The number of block to read (default: 1)

        :return: Block(s)'s content
        """
        request = Request(
            offset=index * self._blocksize,
            length=count * self._blocksize,
        )
        request.to_socket(self._socket)

        response = Response.from_socket(request, self._socket)
        if response.handle != request.handle:
            raise ValueError("unexpected packet received")

        code = response.error
        if code != 0:
            raise OSError(code, strerror(code))

        return response.payload

    def write_block(self, index, blocks):
        """
        Write block(s) at the specified index..

        :arg index: Index of the first block to overwrite
        :arg block: The data to write
        """
        if len(blocks) % self._blocksize != 0:
            raise ValueError(
                'blocks’ length must be a multiple of %d' % self._blocksize
            )

        request = Request(
            offset=index * self._blocksize,
            payload=blocks,
        )
        request.to_socket(self._socket)

        response = Response.from_socket(request, self._socket)
        if response.handle != request.handle:
            raise ValueError("unexpected packet received")

        code = response.error
        if code != 0:
            raise OSError(code, strerror(code))


class bloc_device(object):
    """
    Simple wrapper around `NetBlockDevice` for API compatibility
    """

    def __init__(self, blksize, host, port):
        self._bd = NetBlockDevice(blksize, host, port)

    def read_bloc(self, bloc_num, numofblk=1):
        return self._bd.read_block(bloc_num, numofblk)

    def write_bloc(self, bloc_num, bloc):
        return self._bd.write_block(bloc_num, bloc)


def test():
    blocksize = 16

    bd = bloc_device(blocksize, '127.0.0.1', 5656)

    data = bd.read_bloc(0)
    print(data)
    assert data == 'aaaaaaaaaaaaaaaa'

    bd.write_bloc(0, 'zzzzzzzzzzzzzzzz')

    data = bd.read_bloc(0)
    print(data)
    assert data == 'zzzzzzzzzzzzzzzz'

    bd.write_bloc(0, 'aaaaaaaaaaaaaaaa')

    data = bd.read_bloc(1, 2)
    print(data)
    assert data == 'bbbbbbbbbbbbbbbbcccccccccccccccc'


if __name__ == '__main__':
    test()
