import os
import sys
from struct import *

MAGIC = 0x01312f76
COMPRESSION = ['NO','RLE','ZIPS','ZIP','PIZ','PXR24','B44','B44A']
LINEORDER = ['INCRESING Y','DECREASING Y','RANDOM Y']
PIXELTYPE = ['UINT','HALF','FLOAT']

#{ Constants
COMPRESSION_NONE = 0
COMPRESSION_RLE = 1
COMPRESSION_ZIPS = 2
COMPRESSION_ZIP = 3
COMPRESSION_PIZ = 4
COMPRESSION_PXR24 = 5
COMPRESSION_B44 = 6
COMPRESSION_B44A = 7

LINEORDER_INCREASING_Y = 0
LINEORDER_DECREASING_Y = 1
LINEORDER_RANDOM_Y = 2

PIXELTYPE_UINT = 0
PIXELTYPE_HALF = 1
PIXELTYPE_FLOAT = 2
#} END constants

__all__ = [	'Header', 'Channel', 'ChannelList' ] 

class Channel(object):
	"""A simple stucture holding channel specific information
	
	:note: The quality comparison compares the name, use is_compatible to compare for 
		binary compatibility"""
	__slots__ = (
				'name',
				'type', 
				'x_sampling', 
				'y_sampling', 
				'p_linear'
				)
	def __init__(self, name='', type=PIXELTYPE_HALF, x_sampling=1, y_sampling=1, p_linear=False):
		self.name = name
		self.type = type
		self.x_sampling = x_sampling
		self.y_sampling = y_sampling
		self.p_linear = p_linear
		
	def __repr__(self):
		return "Channel(%s, %s, %i, %i, %i)" % (self.name, PIXELTYPE[self.type], self.x_sampling, self.y_sampling, self.p_linear)
	
	def __eq__(self, rhs):
		return self.name == rhs.name
		
	def __ne__(self, rhs):
		return not self.__eq__(rhs)

	#{ Interface
	
	def is_compatible(self, rhs):
		""":return: True if we are binary compatible to rhs"""
		return self.type == rhs.type and self.x_sampling == rhs.x_sampling and self.y_sampling == rhs.y_sampling
	
	#} END interface

	
class ChannelList(list):
	"""A list of channels - it stores them in order and as efficiently as possible.
	Additional utility methods are provided, similar to the respective c++ implementation
	
	The exr channel list assumes sorted order"""
	__slots__ = tuple()
	
	#{ Interface 
	
	def channels_in_layer(self, layer):
		""":return: list with all name,channel pairs whose layer matches the given layer name"""
		return self.channels_with_prefix(layer+".")
	
	def channels_with_prefix(self, prefix):
		""":return: slice of ourselves with all consecutive Channels which match the given prefix"""
		# we may assume a sorted order
		s = None
		e = 0
		for i, c in enumerate(self):
			if c.name.startswith(prefix):
				if s is None:
					s = i
					e = s + 1
				else:
					e += 1
				#END handle match
			#END if we have a match
		#END for each name in channel
		out = type(self)()
		if s is not None:
			out.extend(self[s:e])
		return out
	
	def channels_with_suffix(self, suffix, case_insensitive=True):
		""":return: HeaderList of all channels which exactly match the given suffix
		:param case_insensitive: If True, the suffix will be matched without honoring the case"""
		if case_insensitive:
			suffix = suffix.lower()
		#END make lower case
		
		out = type(self)()
		for c in self:
			n = case_insensitive and c.name.lower() or c.name
			i = n.rfind('.')
			if i > -1:
				n = n[i+1:]
			if n == suffix:
				out.append(c)
			#END compare suffix
		return out
	
	def layers(self):
		""":return: a list of all layer names, without the terminating 
		'.' character. Empty layer names are skipped."""
		out = set()
		for c in self:
			n = c.name
			i = n.rfind('.')
			if i > -1 and i != 0 and i+1 < len(n):
				out.add(n[:i])
			#END dot is within string
		#END for each name, channel pair
		return sorted(out)
		
	def default_channels(self):
		""":return: a list of Channels which are not in any layer. This includes
		all channels whose names where previously exluded when querying the layer(), but will not
		include empty layers"""
		out = type(self)()
		for c in self:
			n = c.name
			i = n.rfind('.')
			if i < 0:
				out.append(c)
			#END have a non-layer
		#END for each name-channel pair
		return out
	#} END interface
	

class Header(object):
	__slots__ = '_header'
	def __init__(self, fd = None):
		self._header = dict()
		if fd is not None:
			self.read(fd)
	
	def _read_int32(self, read):
		l = read(4)
		return unpack('I', l)[0]
	
	def _read_string(self, read):
		s = ''
		d = read(1)
		while d != '\0':
			s += d
			d = read(1)
		return s
	
	def _conv_data(self, name, data, size):
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
			result = unpack('B', data)[0]
		elif name == 'chlist':
			chld = ChannelList()
			cid = 0
			while cid < (size-1):
				cname = ''
				while data[cid] != '\0':
					cname += data[cid]
					cid = cid + 1
				cid = cid + 1
				ch = unpack('iiii', data[cid:cid+16])
				cid = cid + 16
				chld.append(Channel(cname, ch[0], ch[2], ch[3], ch[1]))
			#END while data is not depleted
			result = chld
		elif name == 'lineOrder':
			result = unpack('B', data)[0]
		else:
			# some data
			result = unpack('%dB' % size, data)
		#END handle type
		return result
	
	
	#{ Interface
	def read(self, fd):
		"""Read the exr header from the given file descriptor and cache the parsed data.
		Existing data will be cleared.
		:param fd: file reader interface, ready for reading
		:return: self
		:raise TypeError: if the header could not understood"""
		self._header = dict()
		read = fd.read
		id = self._read_int32(read)
		ver = self._read_int32(read)
		
		if id != MAGIC:
			raise TypeError("Invalid magic number: %i" % MAGIC)
		#END assert number
		
		attr_name = self._read_string(read)
		while len(attr_name):
			type_name = self._read_string(read)
			size = self._read_int32(read)
			data = read(size)
			
			data = self._conv_data(type_name, data, size)
			
			self._header[attr_name] = (type_name, data)
			attr_name = self._read_string(read)
		#END while reading
		return self
	
	def attribute(self, name):
		""":return: Attribute's data with the given name. It may just be simple data, or 
		more complex one depending on the underlying datatype
		:raise KeyError: if the attributes name was not found"""
		return self.attribute_info(name)[1]
		
	def attribute_info(self, name):
		""":return: tuple of (attr_type_name, data) for the given attribute name
		:raise KeyError: if attribute was not found"""
		return self._header[name]
		
	def attributes(self):
		""":return: list of all available attributes"""
		return self._header.keys()
		
	#}END interface

	#{ Predefined attributes
	
	def channels(self):
		""":return: ChannelList"""
		return self.attribute('channels')
	
	#}END access to predefined attributes

