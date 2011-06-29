from lib import *
import os

from exr.header import *
from exr.header import PIXELTYPE_FLOAT

class TestHeader(TestBase):
	def test_channel(self):
		c = Channel()
		assert c == Channel()
		assert not c != Channel()
		
		c2 = Channel('newone', PIXELTYPE_FLOAT, 2, 3, True)
		assert c != c2
		
		assert not c.is_compatible(c2)
		assert c.is_compatible(c)
		
	def test_reading(self):
		for exr_base in ("mayamr", "mayavray2"):
			exrpath = fixture_path("multi_layer_%s.exr" % exr_base)
			
			hdr = Header(open(exrpath, 'rb'))
			assert hdr.attribute('channels') is hdr.channels()
			
			dtype, channels = hdr.attribute_info('channels')
			assert dtype == 'chlist'
			assert channels is hdr.channels()
			
			assert len(channels) > 15
			
			prefix_channels = channels.channels_with_prefix("shadow")
			assert isinstance(prefix_channels, ChannelList)
			for ch in prefix_channels:
				assert isinstance(ch, Channel)
				#END for each channel
			
			layers = channels.layers()
			assert layers
			assert len(layers) < len(channels)
			for layer_name in layers:
				chans = channels.channels_in_layer(layer_name)
				assert isinstance(chans, ChannelList)
				assert chans
				assert isinstance(chans, list)
				assert not layer_name.startswith('.')
				scount = 0
				for suffix in ('rxaz'):
					scount += len(chans.channels_with_suffix(suffix))
				assert scount
			#END for each layer name
			
			default_channels = channels.default_channels()
			assert default_channels
			assert isinstance(default_channels, ChannelList)
			
			for ch in default_channels:
				assert isinstance(ch, Channel)
				assert ch.name not in layers
				assert '.' not in ch.name, ch.name
			#END for each name
			
			if 'vray2' in exr_base:
				assert ".B" not in layers and "Z" not in layers and 'G' not in layers
			else:
				assert 'G' not in layers
			#END proper verification
		#END for each fixture name
