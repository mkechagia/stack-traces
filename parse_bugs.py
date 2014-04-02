'''
Copyright 2014 Maria Kechagia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import re
import os
import sys

from collections import defaultdict
from odict import OrderedDict
from sets import Set

# dictionary for methods
dict_exc = {}

def main():
	path = "/Users/marki/Desktop/android_bugs/android_platform_bugs.xml"
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	# no of Android bugs titles
	lc = 0
	# no of matched objects
	c = 0
	for l, k in enumerate(lines):
		# issue with exception
		if re.search("<title>", lines[l]):
			lc = lc + 1
			#keep pairs of method-exceptions from android bugs' titles
			matchObj_1 = re.search(r'[a-zA-Z\$]+(Exception|Error)', lines[l])
			matchObj_2 = re.search(r'\s[a-z]+[A-Z][a-z]+[A-Za-z]*', lines[l])
			if matchObj_1 and matchObj_2:
				print matchObj_1.group(), matchObj_2.group()
				c = c + 1
	
	print "no of pairs (with duplicates):", c
	print "no of titles in android bugs:", lc

# run main
if __name__ == '__main__':
	main()
