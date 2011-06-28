from lib import *
import os

from exr.header import *
from exr.header import PIXELTYPE_FLOAT

class TestHeader(TestBase):
	def test_channel(self):
		c = ExrChannel()
		assert c == ExrChannel()
		assert not c != ExrChannel()
		
		c2 = ExrChannel(PIXELTYPE_FLOAT, 2, 3, True)
		assert c != c2
		
	def test_reading(self):
		for name in ("mayamr", "mayavray2"):
			exrpath = fixture_path("multi_layer_%s.exr" % name)
			
			hdr = ExrHeader(open(exrpath, 'rb'))
			assert hdr.attribute('channels') is hdr.channels()
			
			dtype, channels = hdr.attribute_info('channels')
			assert dtype == 'chlist'
			assert channels is hdr.channels()
			
			assert len(channels) > 15
			
			# test ExrChannels
			if 'vray' in name:
				pass
			else:
				pass
			#END exr name specific tests
		#END for each fixture name
