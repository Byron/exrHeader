from unittest import TestCase

import os
import sys
import tempfile

#{ Utilities

def maketemp(*args, **kwargs):
	"""Wrapper around default tempfile.mktemp to fix an osx issue"""
	tdir = tempfile.mktemp(*args, **kwargs)
	if sys.platform == 'darwin':
		tdir = '/private' + tdir
	return tdir

def fixture_path(name):
	""":return:
		path to fixture file with ``name``, you can use a relative path as well, like
		subfolder/file.ext"""
	return os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/%s" % name))

#} END utiltiies


#{ Classes

class TestBase(TestCase):
	"""Base test case for all oms specific tests"""
	
	
#} END classes
