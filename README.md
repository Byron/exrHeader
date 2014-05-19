[![Build Status](https://travis-ci.org/Byron/exrHeader.svg?branch=master)](https://travis-ci.org/Byron/exrHeader)
[![Coverage Status](https://coveralls.io/repos/Byron/exrHeader/badge.png)](https://coveralls.io/r/Byron/exrHeader)

This is OpenEXR header loader.

## Usage Examples

### Collecting attributes

```python
from exrHeader import *

fd = open('sample.exr','rb')
exr = ExrHeader()
if exr.read(fd):
    print exr.attributes()
fd.close()
```

### Get channel list

```python
from exrHeader import *

fd = open('sample.exr','rb')
exr = ExrHeader()
if exr.read(fd):
    chlist = exr.getAttr('channels')['chlist']
    for ch in chlist:
        print "%s:%s" % (ch, chlist[ch])
fd.close()
```

### scanline or tiles

```python
from exrHeader import *

fd = open('sample.exr', 'rb')
exr = ExrHeader()
if exr.read(fd):
    if not exr.getAttr('tiles'):
        print("scanline")
    else:
        print("tiles")
else:
    print( "unknown file or error" )
fd.close()
```


