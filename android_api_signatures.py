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

from odict import OrderedDict
from sets import Set
from collections import defaultdict

# dictionary for android api methods (from source code)
global api_methods
# dictionary for stacktrace methods
global stacktrace_methods

# initialization
api_methods = {}
stacktrace_methods = {}

def main():
	# methods from Android API source code-level 15
	api_path = "/Users/marki/Desktop/items/stackoverflow_bugs/set1_android_api_methods.txt"
	# methods from signatures-android
	api_methods_stacktraces_path = "/Users/marki/Desktop/android_methods.txt"
	# methods from signatures-java
	api_methods_stacktraces_path1 = "/Users/marki/Desktop/java_methods.txt"

	# find common methods in API source code and signatures
	read_api_methods(api_path)
	print "no of distinct API methods in source code:", len(api_methods.keys())
	read_stacktrace_methods(api_methods_stacktraces_path)
	print "no of distinct methods in signatures:", len(stacktrace_methods.keys())
	compare_api_stack_trace_methods()

# keep unique methods from android api methods (source code)
def read_api_methods(path):
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	# for each line
	for l, k in enumerate(lines):
		# clean methods
		methods = lines[l].split("\n")
		# for each method in the list
		for m, n in enumerate(methods):
			# check if the method exists already in the dictionary
			# and increase its frq if there exist more than one times
			d_keys = api_methods.keys()
			if methods[m] in d_keys:
				values = api_methods.get(methods[m])
				values = values + 1
				api_methods[methods[m]] = values
			else:
				api_methods.setdefault(methods[m], 1)

# extract methods from stack traces
def read_stacktrace_methods(path):
	c = 0
	# open and read file
	k = open(path)
	# add lines to a list
	lines_m = k.readlines()
	# for each line
	for l, k in enumerate(lines_m):
		# list of methods from stack traces 
		# use "\n" or "\r" depending the txt file
		mtds = lines_m[l].split("\n")
		# split methods to get the last element 
		spl_mtd = mtds[0].split(".")
		last_method_elem = spl_mtd[len(spl_mtd)-1]
		# add method to dictionary
		s_keys = stacktrace_methods.keys()
		c = c + 1
		if last_method_elem in s_keys:
			values = stacktrace_methods.get(last_method_elem)
			values = values + 1
			stacktrace_methods[last_method_elem] = values
		else:
			stacktrace_methods.setdefault(last_method_elem, 1)

	print "no of signature methods (with duplicates)", c

def compare_api_stack_trace_methods():
	api_keys = api_methods.keys()
	st_keys = stacktrace_methods.keys()
	# new set with elements in stack traces but not in the api documentation
	undoc_methods = list(Set(st_keys).difference(Set(api_keys)))
	print undoc_methods
	print "no of undoc_methods: ", len(undoc_methods)

# run main
if __name__ == '__main__':
	main()