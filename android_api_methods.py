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

# This file finds methods (protected/private) from the Android API documentation 
# Except for the methods, we find exceptions. 

import re
import os
import sys

from collections import defaultdict
from odict import OrderedDict
from sets import Set

# dictionary of triplets
global m_dict
# for the java files with API reference
global api_jav
# for methods and exceptions (@throws and signature exceptions) in java files (source code)
global st_dict
# for the exceptions found in the file with the API methods (triples from stack traces)
global exceptions
# for all the exceptions found in the Android API source code
global exceptions_dict

# initialization
m_dict = OrderedDict([])
api_jav = []
st_dict = OrderedDict([])
exceptions = {}
exceptions_dict = OrderedDict([])

def main():
	# directory for the online API documented Android classes
	cl_path = "/Users/marki/PHD/MSR14/api-exceptions/classes_api_without_embedded_classes_unique.txt"
	api_clas = read_path(cl_path)

	# directory for the android package (source code ver. 15)
	pkg_path = "/Users/marki/Programs/adt-bundle-mac-x86_64-20130514/sdk/sources/android-15/"
	read_folder(pkg_path, api_clas)

	print "Total no of unique methods (with/without exceptions): ", len(st_dict.keys())
	keys = st_dict.keys()
	for k, s in enumerate(keys):
		print keys[k] 

# add the classes of the file in a list: 2631 API classes
def read_path(path):
	# list for classes in file
	cl_list = []
	f = open(path)
	# add lines to a list
	lines = f.readlines()
	for l, k in enumerate(lines):
		sp = re.split("\s", lines[l])
		cl_list.append(sp[0])
	return cl_list

# search java files that have API documentation
def read_folder(path, api_clas):
	for subdir, dirs, files in os.walk(path):
		for file in files:
			# search only for files that end with .java
			e = re.search("\.java$", file)
			if e:
				fl = re.split("\.", file)
				if (fl[0] in api_clas):
					# list with java files that have these class names in documentation
					api_jav.append(fl[0])
					# .java2.txt created using the doclet and have only the public and protected methods
					p = subdir + "/" + fl[0] + ".java2.txt"
					# use either methods with args or without: the default is without args
					#file_methods_arg(p)
					file_methods(p)

# update dictionary with methods and their exceptions from java files
def file_methods(file):
	# dictionary for current examined method 
	dict = {}
	# exceptions dictionary for current examined method (not first time values included)
	b = {}
	d = {}
	# exceptions dictionary for method (first time values included only)
	a = {}
	e = {}
	# if the method has already being examined
	isNew = False

	f = open(file)
	#print file
	lines = f.readlines()
	# to distinguish next method
	c = 0
	for l, k in enumerate(lines):
		if re.search("Method:", lines[l]):
			c = c + 1
			# keep only the method name
			mthd_nm_arg = re.split(":", lines[l])
			mthd_nm = re.split("\(", mthd_nm_arg[1])
			#print mthd_nm_arg[1]
			# check if the method exists in the dictionary
			if (mthd_nm[0] in st_dict.keys()):
				isNew = False
				dict = st_dict.get(mthd_nm[0])
				b = dict.get("Throws")
				a = dict.get("init_Throws")
				d = dict.get("Exceptions")
				e = dict.get("init_Exceptions")
			elif (mthd_nm[0] not in st_dict.keys()):
				isNew = True
				st_dict.setdefault(mthd_nm[0], dict)
				a = dict.setdefault("init_Throws", [])
				b = dict.setdefault("Throws", [])
				e = dict.setdefault("init_Exceptions", [])
				d = dict.setdefault("Exceptions", [])
				u = dict.setdefault("Union", [])
			# check if the next line has method or exceptions
			if ((l + 1) < len(lines)):
				if re.search("(Hidden|Method)", lines[l+1]):
					#print "find method", mthd_nm_arg[1]
					# case: @hide method
					if re.search("Hidden", lines[l+1]):
						dict.setdefault("Hidden", [])
					# case: method initially has exceptions but next time it hasn't got 
					if ((not isNew) and ((not b) and a)):
						#print "w"
						dict.setdefault("Change", []).append("T")
					if ((not isNew) and ((not d) and e)):
						#print "w"
						dict.setdefault("Change", []).append("E")
					c = 0
					dict = {}
					isNew = False
		# check if the next line of the method has exceptions: new/old method
		elif ((re.search("Throws", lines[l])) and (c == 1) and (isNew)):
			#print "thr"
			# keep exception name
			thr = re.split(":", lines[l])
			th = re.split("\n", thr[1])
			if (th[0] not in a):
				dict.setdefault("init_Throws", []).append(th[0])
			if ((l + 1) < len(lines)):
				if re.search("Method:", lines[l + 1]):
					c = 0
					dict = {}
					isNew = False
					continue
		elif ((re.search("Throws", lines[l])) and (c == 1) and (not isNew)):
			#print "ok"
			thr = re.split(":", lines[l])
			th = re.split("\n", thr[1])
			if (th[0] not in b):
				dict.setdefault("Throws", []).append(th[0])
				b = dict.get("Throws")
			if ((l + 1) < len(lines)):
				if re.search("Method:", lines[l + 1]) or (re.search("^\s*$", lines[l + 1])):
					#print a, b
					# case: the set of values of old method (b) is different from the initial values (a) 
					if (not Set(b).issubset(Set(a))):
						dict.setdefault("Change", []).append("T")
						#print Set(b).issubset(Set(a))
					c = 0
					dict = {}
					continue
		# check if the next line of the method has exceptions: new/old method
		elif ((re.search("Exception:", lines[l])) and (c == 1) and (isNew)):
			# keep exception name
			thr = re.split(":", lines[l])
			th = re.split("\n", thr[1])
			if (th[0] not in e):
				dict.setdefault("init_Exceptions", []).append(th[0])
			if ((l + 1) < len(lines)):
				if re.search("Method:", lines[l + 1]):
					c = 0
					dict = {}
					isNew = False
					continue
		elif ((re.search("Exception:", lines[l])) and (c == 1) and (not isNew)):
			thr = re.split(":", lines[l])
			th = re.split("\n", thr[1])
			if (th[0] not in d):
				dict.setdefault("Exceptions", []).append(th[0])
				d = dict.get("Exceptions")
			if ((l + 1) < len(lines)):
				if re.search("Method:", lines[l + 1]) or (re.search("^\s*$", lines[l + 1])):
					# case: the set of values of old method (d) is different from the initial values (e) 
					if (not Set(d).issubset(Set(e))):
						dict.setdefault("Change", []).append("E")
					c = 0
					dict = {}
					continue


# run main
if __name__ == '__main__':
	main()