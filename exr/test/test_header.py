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
			
			for name, ch in channels.channels_with_prefix("shadow"):
				assert isinstance(name, basestring)
				assert isinstance(ch, ExrChannel)
				#END for each channel
			
			layers = channels.layers()
			assert layers
			assert len(layers) < len(channels)
			for layer_name in layers:
				chans = channels.channels_in_layer(layer_name)
				assert chans
				assert isinstance(chans, list)
			#END for each layer name
		#END for each fixture name
