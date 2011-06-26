import os
import sys
from struct import *

MAGIC = 0x01312f76
COMPRESSION = ['NO','RLE','ZIPS','ZIP','PIZ','PXR24','B44','B44A']
LINEORDER = ['INCRESING Y','DECREASING Y','RANDOM Y']
PIXELTYPE = ['UINT','HALF','FLOAT']

__all__ = ['ExrHeader']

class ExrHeader(object):
	__slots__ = '_header'
	
	def __init__(self, fd = None):
		self._header = list()
		if fd is not None:
			self.read(fd)
	
	def read_int32(self, read):
		l = read(4)
		return unpack('I', l)[0]
	
	def read_string(self, read):
		s = ''
		d = read(1)
		while d != '\0':
			s += d
			d = read(1)
		return s
	
	def conv_data(self, name, data, size):
		result = ""
		if name == 'int':
			result = unpack('i', data)[0]
		elif name == 'float':
			result = unpack('f', data)[0]
		elif name == 'double':
			result = unpack('d', data)[0]
		elif name == 'string':
			result = "%s" % data
		elif name == 'box2i':
			result = unpack('4i', data)
		elif name == 'v2i':
			result = unpack('2i', data)
		elif name == 'v2f':
			result = unpack('2f', data)
		elif name == 'v3i':
			result = unpack('3i', data)
		elif name == 'v3f':
			result = unpack('3f', data)
		elif name == 'compression':
			result = COMPRESSION[unpack('B', data)[0]]
		elif name == 'chlist':
			chld = list()
			cid = 0
			while cid < (size-1):
				cname = ''
				while data[cid] != '\0':
					cname += data[cid]
					cid = cid + 1
				cid = cid + 1
				ch = unpack('iiii', data[cid:cid+16])
				cid = cid + 16
				chld.append((cname, {'pixeltype':PIXELTYPE[ch[0]], 'sampling x':ch[2], 'sampling y':ch[3]}))
			result = chld
		elif name == 'lineOrder':
			result = LINEORDER[unpack('B', data)[0]]
		else:
			result = unpack('%dB' % size, data)
		
		return result
	
	def read(self, fd):
		self._header = list()
		read = fd.read
		id = self.read_int32(read)
		ver = self.read_int32(read)
		
		if id != MAGIC:
			return False
		
		cn = self.read_string(read)
		while len(cn):
			name = self.read_string(read)
			size = self.read_int32(read)
			data = read(size)
			
			data = self.conv_data(name, data, size)
			
			self._header.append((cn, name, data))
			cn = self.read_string(read)
		
		return True
	
	def get(self):
		return self._header
		
	def __getattr__(self, attr):
		for name, dtype, data in self._header:
			if name == attr:
				return (dtype, data)
		#END serach for matching attribute name
		return super(ExrHeader, self).__getattr__(attr)
	
	def attributes(self):
		return [t[0] for t in self._header]
		

