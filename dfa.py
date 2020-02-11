"""Command line tool to determine the equivalence of DFAs"""
# Theory of Computation Coursework
# Equivalence of DFAs

import sys


def read_DFA(filepath):
	'''Read input file with encoded DFA, and return DFA dictionary'''

	# get lines array
	with open(filepath, "r") as file:
		lines = file.readlines()

	# strip whitespace
	lines = [line.strip() for line in lines]

	# get encoded DFA parameters
	num_states = lines[0]
	states = lines[1].split()
	alph_size = lines[2]
	alph = lines[3].split()
	tf_lines = lines[4: (4+int(num_states))]
	start_state = lines[4+int(num_states)]
	num_accepts = lines[5+int(num_states)]

	# account for dfas with no accept states
	if num_accepts == '0':
		accepts = []
	else:
		accepts = lines[6 + int(num_states)].split()

	# split transition function into list of lists
	tf_lines = [line.split() for line in tf_lines]

	# set up transitions dictionary: (state, symbol) > resulting state
	tf_dict = {}
	for i in range(0, len(states)):
		for j in range(0, len(alph)):
			tf_dict[ (states[i], alph[j]) ] = tf_lines[i][j]

	# create dfa dictionary
	dfa = { 
			'states':		states,
			'alph':			alph,
			'tf':			tf_dict,
			'start_state':	start_state,
			'accepts':		accepts 
		}

	return dfa


def print_encoding(d):
	'''Print DFA in encoded format'''

	print(len(d['states']))

	for state in d['states']:
		print(state, end=' ')
	print()

	print(len(d['alph']))

	for symbol in d['alph']:
		print(symbol, end=' ')
	print()

	for state in d['states']:
		for symbol in (d['alph']):
			print(d['tf'][(state, symbol)], end=' ')
		print()

	print(d['start_state'])

	print(len(d['accepts']))

	for a in d['accepts']:
		print(a, end=' ')
	print()


def print_dfa(d):
	'''Verbose prints DFA, row by row with parameters'''

	for i in d:
		if i == 'tf':
			print("transition function (state + symbol = new state):")
			for t in d[i]:
				print(t[0],'+',t[1],'=',d[i][t])
		else:
			print(str(i)+": "+str(d[i]))


def complement(d):
	'''Returns the complement of input DFA (by swapping accept states)'''

	comp_accepts = []

	# for each node in d:
	for i in d['states']:
		# if node is not an accept state in d, add to complement
		if i not in d['accepts']:
			comp_accepts.append(str(i))

	# create comp dfa
	comp_dfa = { 
			'states':		d['states'],
			'alph':			d['alph'],
			'tf':			d['tf'],
			'start_state':	d['start_state'],
			'accepts':		comp_accepts 
		}

	return comp_dfa


def transition(dfa, state, symbol):
	'''Returns state resulting from state + symbol'''

	new_state = dfa['tf'][(state, symbol)]
	return new_state


def intersection(d1, d2):
	'''Returns the intersection of 2 given DFAs- i.e. language accepted by both'''

	# Q* = set of pairs (r,s) where r is a state in d1, and s is a state in d2
	Q = []
	for r in d1['states']:
		for s in d2['states']:
			Q.append('{}{}'.format(r,s))

	# tf* = for each state (r,s) and symbol c: tf((r,s),c) = (d1_tf(r,c), d2_tf(s,c))
	tf = {}
	for (r,s) in Q:
		for c in d1['alph']:
			tf[('{}{}'.format(r,s)),c] = '{}{}'.format(transition(d1,r,c), transition(d2,s,c))

	# start state q0* = (d1_q0, d2_q0)
	start_state = '{}{}'.format(d1['start_state'],d2['start_state'])

	# accept states F* = set of pairs (r,s) where r is accept in d1, AND s is accept in d2
	accepts = []
	for r in d1['accepts']:
		for s in d2['accepts']:
			accepts.append('{}{}'.format(r,s))

	# alphabet (should be same for both dfas, otherwise error, return)
	if d1['alph'] == d2['alph']:
		alph = d1['alph']
	else:
		print("error- alphabets don't match")
		return

	intersection_dfa = {
			'states':		Q,
			'alph':			alph,
			'tf':			tf,
			'start_state':	start_state,
			'accepts':		accepts 
			}

	return intersection_dfa


def union(d1, d2):
	'''Returns the union of 2 given DFAs - i.e. a DFA that accepts d1 or d2'''

	d3 = intersection(d1,d2)

	accepts = []
	for r in d1['states']:
		for s in d2['states']:
			if (r in d1['accepts']) or (s in d2['accepts']):
				accepts.append('{}{}'.format(r,s))

	d3['accepts'] = accepts

	return d3


def symmetric_difference(d1, d2):
	'''Returns the symmetric difference of 2 DFAs- i.e. accepted in one and not other'''
	
	dfa_union = union(d1, d2)
	dfa_int = intersection(d1, d2)

	a1 = dfa_union['accepts']
	a2 = dfa_int['accepts']

	dfa_sym = dfa_union
	dfa_sym['accepts'] = set(a1)^set(a2)

	return dfa_sym


def non_empty(d):
	'''Returns whether the language of d is empty- i.e. is there a transition from start to accept state'''
	
	path = ""
	queue = [(d['start_state'], path)]
	visited = [d['start_state']]

	# while queue is not empty- i.e. we haven't visited all nodes
	while len(queue) != 0:

		# pop first item from queue
		current_state = queue.pop(0)

		# if accept state found, return path
		if current_state[0] in d['accepts']:
			if current_state[1] == "":
				print('language non-empty - \'e\' accepted')
			else:
				print('language non-empty - \'{}\' accepted'.format(current_state[1]))
			return

		# populate queue with adjacent nodes
		for symbol in d['alph']:
			state = transition(d, current_state[0], symbol)

			if state not in visited:
				visited.append(state)
				updated_path = current_state[1] + symbol
				queue.append((state, updated_path))

	# if no items left in queue and accept state not found- language is empty
	print('language empty')	


def equivalent(d1, d2):
	'''Returns whether 2 given DFAs are equivalent, i.e. whether they accept the same language'''

	start_state = '{}{}'.format(d1['start_state'], d2['start_state'])	
	queue = [start_state]
	visited = [start_state]

	# check that alphabets match
	if d1['alph'] != d2['alph']:
		print('alphabets don\'t match')
		return
	else:
		alph = d1['alph']

	# while queue is not empty:
	while len(queue) != 0:

		# pop first item in queue
		current_state = queue.pop(0)

		# check if both states are accept/intermediate states- i.e. equivalent
		d1_accept = current_state[0] in d1['accepts']
		d2_accept = current_state[1] in d2['accepts']

		if d1_accept != d2_accept:
			print('not equivalent')
			return

		# for each symbol in alph- calculate next state
		for symbol in alph:
			d1_state = transition(d1, current_state[0], symbol)
			d2_state = transition(d2, current_state[1], symbol)
			state = '{}{}'.format(d1_state, d2_state)

			# if state not previously visited- add to queue
			if state not in visited:
				visited.append(state)
				queue.append(state)

	print('equivalent')	


def main(args):
	'''Command line interpreter'''

	if len(args) == 1:
		print("no args given")
		return

	else:
		# TASK 1: complement [D]
		# print to screen the DFA that recognises only all strings rejected by input DFA
		if args[1] == "complement":
			d1 = read_DFA(args[2])
			c = complement(d1)
			print_encoding(c)

		# TASK 2: intersection [D1] [D2]
		# print to screen the DFA that recognises only strings accepted by both D1 & D2
		elif args[1] == "intersection":
			d1 = read_DFA(args[2])
			d2 = read_DFA(args[3])
			i = intersection(d1, d2)
			print_encoding(i)

		# TASK 3: symmetric difference [D1] [D2]
		# return DFA that recognises strings accepted by only 1 of DFAs
		elif args[1] == "difference":
			d1 = read_DFA(args[2])
			d2 = read_DFA(args[3])
			d = symmetric_difference(d1, d2)
			print_encoding(d)

		# TASK 4: non-emptyness [DFA]
		# return whether L(d) is empty- i.e. is there a transition from start to accept state
		elif args[1] == "empty":
			d1 = read_DFA(args[2])
			non_empty(d1)

		# TASK 5: equivalence [D1] [D2]
		# returns whether 2 given dfas are equivalent, i.e. whether they accept the same language
		elif args[1] == "equivalent":
			d1 = read_DFA(args[2])
			d2 = read_DFA(args[3])
			e = equivalent(d1, d2)


# run main with sys args
args = sys.argv
main(args)
