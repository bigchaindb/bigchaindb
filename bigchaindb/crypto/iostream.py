import base64
import hashlib
from math import ceil

import binascii

from six import string_types

MSB = 0x80
REST = 0x7F
MSBALL = ~REST
INT = 2**31

# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER
MAX_SAFE_INTEGER = 2**53-1


class UnsignedLEB128:
    """
    Adapter for DWARF unsigned LEB128.

    A VARUINT is a variable length integer encoded as base128 where the highest
    bit indicates that another byte is following. The first byte contains the
    seven least significant bits of the number represented.

    see: https://en.wikipedia.org/wiki/LEB128 (ULEB128)
    see http://grokbase.com/t/python/python-list/112e5jpc16/encoding

    """
    @staticmethod
    def encode(obj):
        out = []
        value = int(obj)
        while value > INT:
            out.append((value & REST) | MSB)
            value /= 7

        while value & MSBALL:
            out.append((value & REST) | MSB)
            value >>= 7

        out.append(value | 0)
        return out

    @staticmethod
    def decode(obj):
        value = 0
        for b in reversed(obj):
            value = value * 128 + (ord(b) & 0x7F)
        return value


class Writer:

    def __init__(self):
        self.components = []

    def write_var_uint(self, value):
        """
        Write a VARUINT to the stream.

        Args:
            value (int): Integer to represent.
        """
        out = UnsignedLEB128.encode(value)
        self.write(out)

    def write_var_bytes(self, buffer):
        """
        Write a VARBYTES.

        A VARBYTES field consists of a VARUINT followed by that many bytes.

        Args:
            buffer (Buffer): Contents of the VARBYTES.
        """
        self.write_var_uint(len(buffer))
        self.write(buffer)

    def write(self, in_bytes):
        """
        Write a series of raw bytes.

        Adds the given bytes to the output buffer.

        Args:
            in_bytes (Buffer): Bytes to write.
        """
        out = in_bytes
        if isinstance(out, (list, bytearray)):
            out = binascii.unhexlify(''.join('{:02x}'.format(x) for x in out))
        if not isinstance(out, bytes):
            out = out.encode('utf-8')
        self.components.append(out)


class Hasher(Writer):

    def __init__(self):
        self.hash = None
        super().__init__()

    def __init__(self, algorithm):
        if algorithm == 'sha256':
            self.hash = hashlib.sha256()
        else:
            raise NotImplementedError
        super(Writer, self).__init__()
    
    def write(self, in_bytes):
        """
        Adds bytes to the hash input.
        
        The hasher will pass these bytes into the hashing function. By overriding
        the Writer class and implementing this method, the Hasher supports any of
        the datatypes that a Writer can write.
        
        Args:
            in_bytes (Buffer): Bytes to add to the hash.
        """
        out = in_bytes
        if isinstance(out, (list, bytearray)):
            out = binascii.unhexlify(''.join('{:02x}'.format(x) for x in out))
        if not isinstance(out, bytes):
            out = out.encode('utf-8')
        self.hash.update(out)

    def digest(self):
        """
        Return the hash.

        Returns the finished hash based on what has been written to the Hasher so far.

        Return:
            Buffer: Resulting hash.
        """
        return self.hash.digest()

    @staticmethod
    def length(algorithm):
        """
        Get digest length for hashing algorithm.

        Args:
            algorithm (string): Hashing algorithm identifier.

        Return:
            int: Digest length in bytes.
        """
        return len(Hasher(algorithm).digest())


class Predictor:

    def __init__(self):
        self.size = 0

    def write_var_uint(self, val):
        """
        Calculate the size of a VARUINT.

        A VARUINT is a variable length integer encoded as base128 where the highest
        bit indicates that another byte is following. The first byte contains the
        seven least significant bits of the number represented.

        Args:
            val (int): Integer to be encoded
        """
        
        if val == 0:
            self.size += 1
        elif val < 0:
            raise ValueError('Variable length integer cannot be negative')
        elif val > MAX_SAFE_INTEGER:
            raise ValueError('Variable length integer too large')
        else:
            # Calculate number of bits divided by seven
            self.size += ceil(len('{:02b}'.format(val)) / 7)

    def write_var_bytes(self, val):
        """
        Calculate the size of a VARBYTES.

        A VARBYTES field consists of a VARUINT followed by that many bytes.

        Args:
            val (varbytes): Contents for VARBYTES
        """
        self.write_var_uint(len(val))
        self.size += len(val)

    def skip(self, in_bytes):
        """
        Add this many bytes to the predicted size.

        Args:
            in_bytes (int): Number of bytes to pretend to write.
        """
        self.size += in_bytes


class Reader:

    def __init__(self, buffer):
        self.buffer = buffer
        self.cursor = 0
        self.bookmarks = []

    @staticmethod
    def from_source(source):
        """
        Create a Reader from a source of bytes.

        Currently, this method only allows the creation of a Reader from a Buffer.

        If the object provided is already a Reader, that reader is returned as is.

        Args:
            source (Reader|Buffer): Source of binary data.
        Return:
            Reader: Instance of Reader
        """
        # if (Buffer.isBuffer(source)) {
        # return new Reader(source)
        # } else {
        # throw new Error('Reader must be given a Buffer')
        if isinstance(source, Reader):
            return source
        return Reader(source)

    def bookmark(self):
        """
        Store the current cursor position on a stack.
        """
        self.bookmarks.append(self.cursor)

    def restore(self):
        """
        Pop the most recently bookmarked cursor position off the stack.
        """
        self.cursor = self.bookmarks.pop()

    def ensure_available(self, num_bytes):
        """
        Ensure this number of bytes is buffered.

        This method checks that the given number of bytes is buffered and available
        for reading. If insufficient bytes are available, the method throws an `OverflowError`.

        Args:
            num_bytes (int): Number of bytes that should be available.
        """
        if len(self.buffer) < self.cursor + num_bytes:
            raise OverflowError('Tried to read {} bytes, but only {} bytes available'
                                .format(num_bytes, len(self.buffer.length) - self.cursor))

    def read_uint8(self):
        """
        Read a single unsigned 8 byte integer.
        
        Return: {Number} Contents of next byte.
        """
        self.ensure_available(1)
        value = self.buffer[self.cursor]
        self.cursor += 1
        return value

    def peek_uint8(self):
        """
        Look at the next byte, but don't advance the cursor.
        
        Return: {Number} Contents of the next byte.
        """
        self.ensure_available(1)
        return self.buffer.read_uint8(self.cursor)

    def skip_uint8(self):
        """
        Advance cursor by one byte.
        """
        self.cursor += 1

    def read_var_uint(self):
        """
        Read a VARUINT at the cursor position.
        
        A VARUINT is a variable length integer encoded as base128 where the highest
        bit indicates that another byte is following. The first byte contains the
        seven least significant bits of the number represented.
        
        Return the VARUINT and advances the cursor accordingly.
        
        Return: {Number} Value of the VARUINT.
        """
        shift = 0
        result = 0
        
        while True:
            in_byte = self.read_uint8()
            
            result += (in_byte & REST) << shift if shift < 28 else (in_byte & REST) * (2 ** shift)
            
            shift += 7
            
            # Don't allow numbers greater than Number.MAX_SAFE_INTEGER
            if shift > 45:
                raise ValueError('Too large variable integer')
            
            if not (in_byte & MSB):
                break

        return result

    def peek_var_uint(self):
        """
        Read the next VARUINT, but don't advance the cursor.
        
        Return: {Number} VARUINT at the cursor position.
        """
        self.bookmark()
        value = self.read_var_uint()
        self.restore()
    
        return value

    def skip_var_uint(self):
        """
        Skip past the VARUINT at the cursor position.
        """
        # Read variable integer and ignore output
        self.read_var_uint()

    def read_var_bytes(self):
        """
        Read a VARBYTES.
        
        A VARBYTES field consists of a VARUINT followed by that many bytes.
        
        Return: {Buffer} Contents of the VARBYTES.
        """
        return self.read(self.read_var_uint())
  
    def peek_var_bytes(self):
        """
        Read a VARBYTES, but do not advance cursor position.
        
        Return: {Buffer} Contents of the VARBYTES.
        """
        self.bookmark()
        value = self.read_var_bytes()
        self.restore()

        return value

    def skip_var_bytes(self):
        """
        Skip a VARBYTES.
        """
        self.skip(len(self.read_var_bytes()))

    def read(self, num_bytes):
        """
        Read a given number of bytes.
        
        Returns this many bytes starting at the cursor position and advances the
        cursor.
        
        Args:
            num_bytes (int): Number of bytes to read.

        Return:
            Contents of bytes read.
        """
        self.ensure_available(num_bytes)
    
        value = self.buffer[self.cursor:self.cursor + num_bytes]
        self.cursor += num_bytes
    
        return value
    
    def peek(self, num_bytes):
        """
        Read bytes, but do not advance cursor.
        
        Args:
             num_bytes (int): Number of bytes to read.

        Return:
            Contents of bytes read.
        """

        self.ensure_available(num_bytes)

        return self.buffer.slice(self.cursor, self.cursor + num_bytes)

    def skip(self, num_bytes):
        """
        Skip a number of bytes.
        
        Advances the cursor by this many bytes.
        
        Args:
             num_bytes (int): Number of bytes to advance the cursor by.
        """
        self.ensure_available(num_bytes)
    
        self.cursor += num_bytes


def base64_add_padding(data):
    """
    Add enough padding for base64 encoding such that length is a multiple of 4

    Args:
        data: unpadded string or bytes
    Return:
        bytes: The padded bytes

    """

    if isinstance(data, string_types):
        data = data.encode('utf-8')
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'=' * missing_padding
    return data


def base64_remove_padding(data):
    """
    Remove padding from base64 encoding

    Args:
        data: fully padded base64 data
    Return:
        base64: Unpadded base64 bytes

    """
    if isinstance(data, string_types):
        data = data.encode('utf-8')
    return data.replace(b'=', b'')
