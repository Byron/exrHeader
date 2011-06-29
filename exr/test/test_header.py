from lib import *
import os

from exr.header import *
from exr.header import PIXELTYPE_FLOAT

class TestHeader(TestBase):
	def test_channel(self):
		c = ExrChannel()
		assert c == ExrChannel()
		assert not c != ExrChannel()
		
		c2 = ExrChannel('newone', PIXELTYPE_FLOAT, 2, 3, True)
		assert c != c2
		
		assert not c.is_compatible(c2)
		assert c.is_compatible(c)
		
	def test_reading(self):
		for exr_base in ("mayamr", "mayavray2"):
			exrpath = fixture_path("multi_layer_%s.exr" % exr_base)
			
			hdr = ExrHeader(open(exrpath, 'rb'))
			assert hdr.attribute('channels') is hdr.channels()
			
			dtype, channels = hdr.attribute_info('channels')
			assert dtype == 'chlist'
			assert channels is hdr.channels()
			
			assert len(channels) > 15
			
			for ch in channels.channels_with_prefix("shadow"):
				assert isinstance(ch, ExrChannel)
				#END for each channel
			
			layers = channels.layers()
			assert layers
			assert len(layers) < len(channels)
			for layer_name in layers:
				chans = channels.channels_in_layer(layer_name)
				assert chans
				assert isinstance(chans, list)
				assert not layer_name.startswith('.')
			#END for each layer name
			
			default_channels = channels.default_channels()
			assert default_channels
			
			for ch in default_channels:
				assert isinstance(ch, ExrChannel)
				assert ch.name not in layers
			#END for each name
			
			if 'vray2' in exr_base:
				assert ".B" not in layers and "Z" not in layers and 'G' not in layers
			else:
				assert 'G' not in layers
			#END proper verification
		#END for each fixture name
