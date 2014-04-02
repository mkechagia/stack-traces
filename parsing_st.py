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

# This program gets csv files of stack traces as an input and parses them.
# Then, it produces txt files with the stack traces in a particular form. 
# Also, in the end, the program prints some statistics about the dataset. 

import sys
import csv
import re
import os

from collections import defaultdict
from odict import OrderedDict

# for storage of a single stack trace; 
# exception levels (keys) and traces (values)
global st_dict
# for the first trace beginning with *at*
global counter
# exception level counter
global ex_counter
# current exception level type
global curr_ex_type
# number of printed stack traces
global no_of_printed_st
# number of empty stack traces
global no_of_empty_st
# number of filtered stack traces (thrown chained exception levels) 
global fl_st_counter
# sequence for exception level chain check
global subseq
# for the number of the stack traces that have unknown exceptions
global u_ex_counter

# variables initialisation
no_of_printed_st = 0 
no_of_empty_st = 0 
fl_st_counter = 0
u_ex_counter = 0

def main():
	# add a forlder with csv files of stack traces
	path = "/Users/marki/Desktop/stack_traces"
	readFolder(path)
	printBasicSTStatistics()

# open the folder given in the path
# and parse each file in it
def readFolder(path):
	for subdir, dirs, files in os.walk(path):
		for file in files:
			# search only for files that end with .csv
			e = re.search("\.csv$", file)
			if e:
				f = path + "/" + file
				parseCSVfile(f)

# parse csv file and process stack traces;
# each stack trace is in a different row into the csv file	
def parseCSVfile(filename):
	global no_of_printed_st
	global no_of_empty_st

	csv.field_size_limit(10000000) # because we deal with huge csv file
	with open(filename, 'rb') as data:
		reader = csv.reader(data)
		try:
			try:
				# create a new file or **overwrite an existing file**.
				new_file = filename.rstrip('.csv') + ".txt"
				print new_file
				f = open(new_file, "w")
			except IOError:
	            		pass
			try:
				for row in reader:
					st_str = "".join(row) # stack trace as string
					st_list = st_str.split("\n") # in list 
					st_dict = keepSTIntoDict(st_list) # in dictionary
					r_st_list = reverseSTDictValues(st_dict) # reversed values for each key
					# print the stack trace only if the reversed list is not empty
					if isr_st_listEmpty(r_st_list) == False:
						printValidST(f, r_st_list)
						checkUnknownExceptionExistence(r_st_list)
						no_of_printed_st = no_of_printed_st + 1 # increase the number of printed stack traces
					else:
						no_of_empty_st = no_of_empty_st + 1 # increase the number of empty stack traces
			finally:
				f.close()
		except csv.Error as e:
			sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

# keep the stack trace into a dictionary;
# set the exception levels as keys;
# put the pure methods (without at), of each exception level,
# into the list of values for this key
def keepSTIntoDict(st_list):
	global st_dict
	global counter
	global ex_counter
	global curr_ex_type
	global fl_st_counter

	# ordered dictionary for the stack trace body
	st_dict = OrderedDict([]) 
	# initialise the variables
	counter = 0
	ex_counter = 0
	curr_ex_type = "type"

	# for each trace from the stack trace
	# check whether it begins with: 1) at, 2) caused by, 3) ...# more, 4) empty line
	for i, t in enumerate(st_list):
		if re.search("^at\s", st_list[i]):
			if processAtTrace(st_list, i) == True:
				st_dict.setdefault(curr_ex_type, []).append(keepOnlyMethod(st_list[i]))
			else:
				break
		elif re.search("Caused\s", st_list[i]) and ex_counter > 0:
			if (i + 1) < len(st_list):
				if checkEndPointExistence(st_list, i + 1, "\.\.\.\s[\d]+\smore") and checkExLevelChain():
					newChainedExLevel(st_list, i)
				else:
					# increase the counter for the filtered stack traces (thrown exception level chain)
					fl_st_counter = fl_st_counter + 1
					break
		elif re.search("\.\.\.\s[\d]+\smore", st_list[i]) and ex_counter > 0:
			# remove last method from values of the current exception type
			st_dict.setdefault(curr_ex_type, []).remove(keepOnlyMethod(st_list[i - 1]))
			# check next trace
			if contAfterMoreTrace(st_list, i) == False:
				break		
		# search for empty lines
		elif re.search("^\s*$", st_list[i]):
			break
		# in the beginning of the stack trace we may have trash, 
		# but we want to continue to the next lines (i.e. next traces)
		else:
			continue
	# return the current stack trace into dictionary
	return st_dict

# process a trace beginning with *at*
# and return true if it is valid, 
# otherwise, return false
def processAtTrace(st_list, i):
	result = True
	global st_dict
	global counter
	global ex_counter
	global curr_ex_type

	if ex_counter < 2:
		if counter == 0:
			if re.search("Caused\s", st_list[i - 1]):
				st_dict.clear() # EMPTY DICTIONARY
				result = False
			else:
				if (checkEndPointExistence(st_list, i, "Caused\s") or checkEndPointExistence(st_list, i, "^\s*$")) and checkExLevelChain():
					newChainedExLevel(st_list, i - 1)
					counter = 1
				else:
					st_dict.clear() # EMPTY DICTIONARY
					result = False
	return result

# check the start point and the end point of the exception level chain
def checkEndPointExistence(st_list, startPoint, l_string):
	global subseq
	result = False
	endPoint = 0
	subseq = []

	if startPoint is not None:
		seq = st_list[startPoint:len(st_list)]
		for s, r in enumerate(seq):
			if s + 1 < len(seq) and re.search(l_string, seq[s + 1]):
				endPoint = s + 1
				subseq = seq[0:endPoint]
				result = True
				break
	return result

# check if between the start point and end point 
# of the exception level chain, we have traces that begin with *at*
def checkExLevelChain():
	result = True
	for l, r in enumerate(subseq):
		if re.search("^at\s", subseq[l]):
			continue
		else:
			result = False
			break
	return result

# add new chained exception level (key) into dictionary
def newChainedExLevel(st_list, i):
	global st_dict
	global ex_counter
	global curr_ex_type

	ex_counter = ex_counter + 1
	curr_ex_type = "!" + keepSTExceptionType(st_list[i]) + str(ex_counter)
	st_dict.setdefault(curr_ex_type, [])

# process a trace beginning with *...#more*
# and return true if it is valid, 
# otherwise, return false
def contAfterMoreTrace(st_list, i):
	result = True
	global st_dict
	global ex_counter
	global curr_ex_type

	# continue only if the next trace (if exists) has *Caused by*
	if (i + 1) < len(st_list):
		if re.search("Caused\s", st_list[i + 1]):
			result = True
		else:
			result = False
	else:
		result = False
	return result

# returns the type of exception 
# 3 levels (when there is caused by):
# HighLevelException/MiddleLevelException/LowLevelException
def keepSTExceptionType(trace):
	exc = re.search("[^\s]+\.+[\w\$\d\.]+(Error|Exception)+.*$", trace)
	if exc and exc is not None :
		return exc.group()
	else:
		return 'bugsense.UnknownException'

# keep everything from the trace except for *at*
def keepOnlyMethod(trace):
	# remove new line from the end of the string
	nl = trace.rstrip('\r')
	# keep everything but "at" and space
	k1 = re.search("[^\s]*\.[\w\$\d]+\.\<init\>\([^)]*\)$", nl)
	k2 = re.search("[^\s]*\.[\w\$\d]+\([^)]*\)$", nl)
	if k1 and k1 is not None:
		# replace .<init> of the trace with 'ctor'
		l1 = re.sub(r'.\<init\>', '.ctor', k1.group())
		# replace part of the trace with ''
		l2 = re.sub(r'\([^)]*\)', '', l1)
		return l2
	elif k2 and k2 is not None:
		# replace part of the trace with ''
		return re.sub(r'\([^)]*\)', '', k2.group())
		
# reverse the list of values for each key in the dictionary
def reverseSTDictValues(st_dict):
	reversedList = [ ]
	# for each key (exception type level) in dictionary
	for k in st_dict.keys():
		for s in reversed(st_dict[k]):
			reversedList.append(s)
		# match anything but the number in the end of the clause
		t = re.search("\![^\s]+\.+[\w\$\d]+(Error|Exception)", k)
		if t is not None:
			reversedList.append(t.group())
	return reversedList

# check if the stack trace list is empty or have None elements
def isr_st_listEmpty(r_st_list):
	result = False
	if len(r_st_list) == 0:
		result = True
	for r in r_st_list:
		if r is None:
			result = True
	return result

# print valid stack traces 
def printValidST(f, r_st_list):
	# for each trace given from the reversed stack trace list
	for tr in r_st_list:
		if tr is not None:
			# write a string to a file and leave space for the next trace
			f.write(tr + " ")
	# add new line at the end of each stack trace
	f.write("\n")

# return the total number of the stack traces 
# that contain at least one unknown exception
def checkUnknownExceptionExistence(r_st_list):
	global u_ex_counter
	for r in r_st_list:
		if re.search("bugsense.UnknownException", r):
			u_ex_counter = u_ex_counter + 1
			break
	return u_ex_counter

# basic statistics about processed stack traces (for the whole dataset)
def printBasicSTStatistics():
	global no_of_printed_st
	global no_of_empty_st
	global fl_st_counter
	global u_ex_counter

	print "This is the no of the printed stack traces: ", no_of_printed_st
	print "This is the no of the empty stack traces: ", no_of_empty_st
	print "This is the no of filtered stack traces: ", fl_st_counter
	print "This is the no of the stack traces which have unknown exceptions: ", u_ex_counter
		
# run main 
if __name__ == "__main__":
	main()	
					





