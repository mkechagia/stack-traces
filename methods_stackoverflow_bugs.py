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
# dictionary for stackoverflow methods
global stackoverflow_methods
# dictionary for methods in bugs
global bugs_methods
# dictionary for stacktrace methods
global stacktrace_methods
# common api methods in source code and stackoverflow
global common_methods_st
# common api methods in source code and bugs
global common_methods_b
# pairs of methods and exceptions
global pairs
# pairs for bugs
global pairs_b

# initialization
api_methods = {}
stackoverflow_methods = {}
bugs_methods = {}
stacktrace_methods = {}
common_methods_st = []
common_methods_b = []
pairs = {}
pairs_b = {}

def main():
	# methods from Android API source code-level 15
	api_path = "/Users/marki/Desktop/stackoverflow_bugs/set1_android_api_methods.txt"
	# titles from stackoverflow 
	stackoverflow_path = "/Users/marki/Desktop/stackoverflow_bugs/titles_stackoverflow.txt"
	# pairs of methods and exceptions from stack overflow
	pairs_stackoverflow = "/Users/marki/Desktop/stackoverflow_bugs/pairs_stackoverflow.txt"
	# methods from signatures
	api_methods_stacktraces_path = "/Users/marki/Desktop/stackoverflow_bugs/api-methods.txt"
	#api_methods_stacktraces_path1 = "/Users/marki/Desktop/android_methods.txt"
	#api_methods_stacktraces_path1 = "/Users/marki/Desktop/java_methods.txt"
	# methods from android bugs
	bugs_path = "/Users/marki/Desktop/statistics_bugs/bugs_methods.txt"
	# pairs of methods and exceptions from android bugs
	pairs_bugs = "/Users/marki/Desktop/statistics_bugs/bugs_pairs.txt"

	# parse API methods
	read_api_methods(api_path)
	print "no of distinct API methods in source code:", len(api_methods.keys())
	# parse stack overflow
	read_stackoverflow_methods(stackoverflow_path)
	print "no of distinct stackoverflow methods:", len(stackoverflow_methods.keys())
	# parse android bugs
	read_bugs_methods(bugs_path)
	print "no of distinct methods in bugs:", len(bugs_methods)
	# parse signatures
	read_stacktrace_methods(api_methods_stacktraces_path)
	print "no of distinct methods in signatures:", len(stacktrace_methods.keys())
	
	# find common methods in API source code and stackoverflow
	compare_api_stackoverflow_methods()
	# find common methods in stack traces and stackoverflow
	compare_stacktrace_stackoverflow_methods_2()
	# pairs of methods-exceptions from stackoverflow that have api methods
	read_stackoverflow_pairs(pairs_stackoverflow)
	#compare_api_stack_trace_methods()
	compare_api_bugs_methods()
	compare_stacktrace_bugs_methods_2()
	read_bugs_pairs(pairs_bugs)

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

# extract methods and their frqs from stack overflow titles
def read_stackoverflow_methods(path):
	c = 0
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	# for each line
	for l, k in enumerate(lines):
		#print lines[l]
		# search for android API methods
		matchObj = re.search(r'[\s][a-z]+[A-Z][a-z]+[A-Za-z]*', lines[l])
		if matchObj:
			# clean method
			mtd = matchObj.group()
			method = mtd.split(" ")
			c = c + 1
			# check if the method exists already in the dictionary
			# and increase its frq if there exist more than one times
			d_keys = stackoverflow_methods.keys()
			if method[1] in d_keys:
				values = stackoverflow_methods.get(method[1])
				values = values + 1
				stackoverflow_methods[method[1]] = values
			else:
				stackoverflow_methods.setdefault(method[1], 1)

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
		mtds = lines_m[l].split("\r")
		for t, r in enumerate(mtds):
			# split methods to get the last element 
			spl_mtd = mtds[t].split(".")
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

# search for stackoverflow methods in api methods
def compare_api_stackoverflow_methods():
	api_keys = api_methods.keys()
	stackoverflow_keys = stackoverflow_methods.keys()

	for e, s in enumerate(api_keys):
		for k, l in enumerate(stackoverflow_keys):
			if api_keys[e] == stackoverflow_keys[k]:
				# append common methods dictionary 
				common_methods_st.append(stackoverflow_keys[k])
				continue
	
	print "no of common API (source code) and stackoverflow methods:", len(common_methods_st)

# search for stackoverflow methods in stacktrace methods
def compare_stacktrace_stackoverflow_methods():
	stacktrace_keys = stacktrace_methods.keys()
	stackoverflow_keys = stackoverflow_methods.keys()

	c = 0
	for e, s in enumerate(stacktrace_keys):
		for k, l in enumerate(stackoverflow_keys):
			if stacktrace_keys[e] == stackoverflow_keys[k]:
				c = c + 1
				del stackoverflow_methods[stackoverflow_keys[k]]
				continue
	
	print "signatures vs. stackoverflow unmatched methods: ", len(keys)
	print "common methods in signatures and stackoverflow: ", c

# search for stackoverflow methods in stacktrace methods. Stackoverflow methods are checked with API methods.
def compare_stacktrace_stackoverflow_methods_2():
	stacktrace_keys = stacktrace_methods.keys()

	c = 0
	for e, s in enumerate(stacktrace_keys):
		for k, l in enumerate(common_methods_st):
			if stacktrace_keys[e] == common_methods_st[k]:
				c = c + 1
				#del common_methods_st[k]
				continue
	
	print "no of common methods in signatures and stackoverflow: ", c

# keep pairs of api methods from stackoverflow
def read_stackoverflow_pairs(path):
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	# counter for method-exceptions pairs
	c = 0
	# counter for methods in the API
	lc = 0
	# for each line
	for l, k in enumerate(lines):
		#print lines[l]
		# clean methods
		methods = lines[l].split("\n")
		method = methods[0].split(" ")
		l_method = method[len(method)-1]
		if (l_method in common_methods_st):
			lc = lc + 1
		# check the method to be in API source methods and in the signatures
		if (l_method in common_methods_st) and (l_method in stacktrace_methods):
			#print method[0], l_method
			pairs.setdefault(l_method, []).append(method[0])
			c = c + 1

	print "no of stackoverflow pairs with api methods: ", lc
	print "no of stackoverflow pairs with methods from signatures: ", c
	#print pairs

# extract methods and their frqs from android bugs
def read_bugs_methods(path):
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	# for each line
	for l, k in enumerate(lines):
		# clean methods
		methods = lines[l].split("\r")
		# for each method in the list
		for m, n in enumerate(methods):
			# check if the method exists already in the dictionary
			# and increase its frq if there exist more than one times
			d_keys = bugs_methods.keys()
			if methods[m] in d_keys:
				values = bugs_methods.get(methods[m])
				values = values + 1
				bugs_methods[methods[m]] = values
			else:
				bugs_methods.setdefault(methods[m], 1)

# search for common methods in android bugs and api source code
def compare_api_bugs_methods():
	api_keys = api_methods.keys()
	bugs_keys = bugs_methods.keys()

	for e, s in enumerate(api_keys):
		for k, l in enumerate(bugs_keys):
			if api_keys[e] == bugs_keys[k]:
				# append common methods dictionary 
				common_methods_b.append(bugs_keys[k])
				continue
	
	print "no of common API (source code) and bugs methods:", len(common_methods_b)

# search for common methods in android bugs and api signatures
def compare_stacktrace_bugs_methods():
	stacktrace_keys = stacktrace_methods.keys()
	bugs_keys = bugs_methods.keys()

	c = 0
	for e, s in enumerate(stacktrace_keys):
		for k, l in enumerate(bugs_keys):
			if stacktrace_keys[e] == bugs_keys[k]:
				c = c + 1
				del bugs_methods[bugs_keys[k]]
				continue
	
	keys = bugs_methods.keys()
	print "signatures vs. bugs unmatched methods: ", len(keys)
	print "common methods in signatures and bugs: ", c

# search for common methods in android bugs and api signatures
def compare_stacktrace_bugs_methods_2():
	stacktrace_keys = stacktrace_methods.keys()

	c = 0
	for e, s in enumerate(stacktrace_keys):
		for k, l in enumerate(common_methods_b):
			if stacktrace_keys[e] == common_methods_b[k]:
				c = c + 1
				continue

	print "no of common methods in signatures and bugs: ", c

# keep pairs of api methods from bugs
def read_bugs_pairs(path):
	# open and read file
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	# counter for method-exceptions pairs
	c = 0
	lc = 0
	# for each line
	for l, k in enumerate(lines):
		#print lines[l]
		# clean methods
		methods = lines[l].split("\n")
		method = methods[0].split(" ")
		l_method = method[len(method)-1]
		if (l_method in common_methods_b):
			lc = lc + 1
		# check the method to be in API source methods and in the signatures
		if (l_method in common_methods_b) and (l_method in stacktrace_methods):
			#print method[0], l_method
			pairs_b.setdefault(l_method, []).append(method[0])
			c = c + 1
	
	print "no of pairs with api methods: ", lc
	print "no of pairs with methods in the api and in signatures", c

def compare_api_stack_trace_methods():
	api_keys = api_methods.keys()
	st_keys = stacktrace_methods.keys()
	undoc_methods = list(Set(st_keys).difference(Set(api_keys)))
	#print undoc_methods
	print "no of undoc_methods: ", len(undoc_methods)

# run main
if __name__ == '__main__':
	main()