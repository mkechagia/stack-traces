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

import xml.etree.ElementTree as ET

from collections import defaultdict
from odict import OrderedDict
from sets import Set

dict_exc = {}

def main():
	path = "/Users/marki/Desktop/stackoverflow_bugs/titles_stackoverflow.txt"
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	c = 0
	for l, k in enumerate(lines):
		matchObj = re.search(r'[a-zA-Z\$]+(e|E)xception', lines[l])
		matchObj2 = re.search(r'\s[a-z]+[A-Z][a-z]+[A-Za-z]*', lines[l])
		if matchObj and matchObj2:
			#print matchObj.group(), matchObj2.group()
			c = c + 1

	print "no of pairs (with duplicates):", c
	print len(lines)
			
# run main
if __name__ == '__main__':
	main()
