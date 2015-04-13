import sys
import collections
import pickle
from collections import defaultdict


def main(corpus_en,corpus_de):
	#read the corpus file from the corpus
	en_corpus = open(corpus_en,"r")
	de_corpus = open(corpus_de,"r")
	#build a dictionary to store the counts, words pair and use english word as 
	en_dict = defaultdict(dict)
	#split the word after reading the line from the corpus
	for en_line in en_corpus:
		#find the corresponding German line
		de_line = de_corpus.readline()
		#split the word as list
		en_words = en_line.split()
		de_words = de_line.split()
		#building up the dictionary
		for en_word in en_words:
			for de_word in de_words:
				en_dict[en_word][de_word] = 0;
				en_dict["NULL"][de_word] = 0;

	en_corpus.close()
	de_corpus.close()
	#initialize the t(f|e)
	for en_word in en_dict.iterkeys():
		for de_word in en_dict[en_word].iterkeys():
				en_dict[en_word][de_word] = 1./len(en_dict[en_word])

	for i in range(0,5):
		print "iteration:" + str(i)


		#Here comes the first loop of em algorithm
		#initialize the counts of english words and en_de words as zero
		en_counts = defaultdict(int)
		en_de_counts = defaultdict(int)
		en_corpus = open(corpus_en,"r")
		de_corpus = open(corpus_de,"r")
		for en_line in en_corpus:
			de_line = de_corpus.readline()
			de_words = de_line.split()
			en_words = en_line.split()
			#english words starts with null
			for de_word in de_words:
				t_counts_sum = en_dict["NULL"][de_word]
				for en_word in en_words:
					t_counts_sum += en_dict[en_word][de_word]

				delta = en_dict["NULL"][de_word]/t_counts_sum
				en_counts["NULL"] = en_counts["NULL"] + delta
				en_de_counts[("NULL",de_word)] = en_de_counts[("NULL",de_word)]+ delta
				for en_word in en_words:
					delta = en_dict[en_word][de_word]/t_counts_sum
					en_counts[en_word] = en_counts[en_word] + delta
					en_de_counts[(en_word,de_word)] = en_de_counts[(en_word,de_word)] + delta

		en_corpus.close()
		de_corpus.close()

		for en_word in en_dict.iterkeys():
			for de_word in en_dict[en_word].iterkeys():
				en_dict[en_word][de_word] = float(en_de_counts[(en_word,de_word)])/en_counts[en_word]

	with open("en_dict","wb") as handle:
		pickle.dump(en_dict, handle)
	#calculate the top 10 words
	en_devword = open("devwords.txt","r")
	top_10_word = open("top_10_word.txt","w")
	for dev_line in en_devword:
		dev_word = dev_line.split()[0]
		de_word = sorted(en_dict[dev_word],key=(en_dict[dev_word]).get,reverse=True)
		de_prob = sorted((en_dict[dev_word]).values(),reverse=True)
		for i in range(0,10):
			top_10_word.write("English word:" + dev_word + "[German word " + str(i) + ":" + str(de_word[i]) + " prob: " + str(de_prob[i]) + "]")
		top_10_word.write("\n")
		top_10_word.write("\n")

	#doing the optimum alignment
	en_corpus = open(corpus_en,"r")
	de_corpus = open(corpus_de,"r")
	alignment_20_sen = open("alignment_20_sen.txt","w")

	for i in range(0,20):
		en_line = en_corpus.readline()
		de_line = de_corpus.readline()
		optimum_alignment = alignment(en_line,de_line,en_dict)
		alignment_20_sen.write("The" + str(i+1) + "sentence's alignment is " + str(optimum_alignment))
		alignment_20_sen.write("\n")

	alignment_20_sen.close()
	en_corpus.close()
	de_corpus.close()

def alignment(en_sentence, de_sentence, en_dict):
	#align the correct order of english words for the de sentence
	en_words = en_sentence.split()
	de_words = de_sentence.split()
	alignment = []
	#iterate through all the german words first
	for de_word in de_words:
		max_t = 0.0
		arg_max_alignment = 0
		#initialize the max_t with the NULL condition
		if de_word in en_dict["NULL"]:
			max_t = en_dict["NULL"][de_word]
		else:
			#if the de_word can not be translated into NULL, it can not use position 0
			max_t = 1
		#use the en_cur_position variable to record the position of english sentence	
		en_cur_position = 1
		for en_word in en_words:
			if de_word in en_dict[en_word]:
				temp_prob = en_dict[en_word][de_word]
			if temp_prob > max_t:
				max_t = temp_prob
				arg_max_alignment = en_cur_position
			en_cur_position += 1

		alignment.append(arg_max_alignment)
	return alignment


if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2])
