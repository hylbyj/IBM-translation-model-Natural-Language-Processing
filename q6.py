import sys
import collections
import pickle
import math
from collections import defaultdict

def main(scrambled_en,original_de):
	de_original = open(original_de,"r")
	outfile = open('unscrambled.en',"w")
	#load all of the things calculated by the previous questions
	with open('en_dict_2', 'rb') as handle:
		en_dict = pickle.load(handle)
	with open('q_2', 'rb') as handle:
		q = pickle.load(handle)    
	#for one de_sentence, loop over all the english sentences
	for de_sentence in de_original:
		en_scrambled = open(scrambled_en,"r")
		best_align_en = ""
		max_prob = -1000000.0
		for en_line in en_scrambled:
			alignment_score = max_alignment(en_line,de_sentence,q,en_dict)
			if alignment_score>max_prob:
				max_prob = alignment_score
				best_align_en = en_line
		outfile.write(str(best_align_en))
		en_scrambled.close()

	de_original.close()
	outfile.close()
#to calculate the score of the alignment
def max_alignment(en_line,de_line,q,en_dict):
	en_words = en_line.split()
	de_words = de_line.split()
	prob_log = 0.0
	l = len(en_words)
	m = len(de_words)
	i = 1
	for de_word in de_words:
		t_max_log = 0.0
		current_log = 0.0
		if de_word in en_dict["NULL"] and (i,l,m) in q:
			current_log = en_dict["NULL"][de_word] * q[(i,l,m)][0]
		if (current_log > t_max_log):
			t_max_log = current_log
		j = 1
		for en_word in en_words:
			if de_word in en_dict[en_word] and (i,l,m) in q:
				current_log = en_dict[en_word][de_word] * q[(i,l,m)][j]
			if (current_log > t_max_log):
				t_max_log = current_log
			j += 1
		i += 1
		if (t_max_log == 0.0):
			prob_log += -100000
		else:
			prob_log += math.log(t_max_log)
	return prob_log

if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2])
