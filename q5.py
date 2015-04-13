import sys
import pickle
import collections
from collections import defaultdict

def main(corpus_en,corpus_de):
	#initialize the q(j|i,l,m)
	with open('en_dict', 'rb') as handle:
		en_dict = pickle.load(handle)	

	en_corpus = open (corpus_en,"r")
	de_corpus = open (corpus_de,"r")
	q = defaultdict(dict)
	for en_line in en_corpus:
		de_line = de_corpus.readline()
		en_words = en_line.split()
		de_words = de_line.split()
		l = len(en_words)
		m = len(de_words)
		for j in range(0,l+1):
			for i in range(1,m+1):
				q[(i,l,m)][j] = 1.0/(l+1)
	en_corpus.close()
	de_corpus.close()
	#here comes the em algorithm, returning en_dict and q
	#initialize the counts
	en_counts = defaultdict(int)
	en_de_counts = defaultdict(int)
	j_ilm_counts = defaultdict(int)
	ilm_counts = defaultdict(int)
	en_dict_2, q_2 = ibm2_em(en_dict,q,corpus_en,corpus_de,en_counts,en_de_counts,j_ilm_counts,ilm_counts)
	
	en_corpus = open(corpus_en,"r")
	de_corpus = open(corpus_de,"r")
	with open("en_dict_2","wb") as handle:
		pickle.dump(en_dict_2, handle)
	with open("q_2","wb") as handle:
		pickle.dump(q_2,handle)
	alignment_20_sen = open("alignment_20_sen_ibm2.txt","w")

	for i in range(0,20):
		en_line = en_corpus.readline()
		de_line = de_corpus.readline()
		optimum_alignment = alignment(en_line,de_line,en_dict_2,q_2)
		alignment_20_sen.write("The" + str(i+1) + "sentence's alignment is " + str(optimum_alignment))
		alignment_20_sen.write("\n")

	alignment_20_sen.close()
	en_corpus.close()
	de_corpus.close()

def ibm2_em(en_dict,q,corpus_en,corpus_de,en_counts,en_de_counts,j_ilm_counts,ilm_counts):
	#interate for 5 times
	for i in range(0,5):
		print "Iteration: " + str(i)
		en_corpus = open(corpus_en,"r")
		de_corpus = open(corpus_de,"r")
		for en_line in en_corpus:
			de_line = de_corpus.readline()
			en_words = en_line.split()
			de_words = de_line.split()
			#start from NULL, update the total 
			l = len(en_words)
			m = len(de_words)
			i = 1
			for de_word in de_words:
				jilm_sum = q[(i,l,m)][0] * en_dict["NULL"][de_word]
				j = 1
				for en_word in en_words:
					jilm_sum += q[(i,l,m)][j] * en_dict[en_word][de_word]
					j += 1
				
				j = 0
				delta = q[(i,l,m)][j] * en_dict["NULL"][de_word]/float(jilm_sum)
				en_counts["NULL"] += delta
				en_de_counts[("NULL",de_word)] += delta
				j_ilm_counts[(j,i,l,m)] += delta
				ilm_counts[(i,l,m)] += delta
				#print str(j_ilm_counts[(j,i,l,m)])
				j += 1
				for en_word in en_words:
					delta = q[(i,l,m)][j] * en_dict[en_word][de_word]/float(jilm_sum)
					#update delta here 
					en_counts[en_word] += delta
					en_de_counts[(en_word,de_word)] += delta
					j_ilm_counts[(j,i,l,m)] += delta
					ilm_counts[(i,l,m)] += delta
					j += 1
				i += 1

		en_corpus.close()
		de_corpus.close()

		for en_word in en_dict.iterkeys():
			for de_word in en_dict[en_word].iterkeys():
				en_dict[en_word][de_word] = float(en_de_counts[(en_word,de_word)])/en_counts[en_word]	
		#not so sure about list key
		for ilm in q.iterkeys():
			for j in q[ilm].iterkeys():
				q[ilm][j] = float(j_ilm_counts[(j,ilm[0],ilm[1],ilm[2])])/ilm_counts[ilm]
				#print str(j_ilm_counts[j,ilm[0],ilm[1],ilm[2]])
	
	return en_dict,q
#calculate the alignment 
def alignment(en_sentence, de_sentence, en_dict,q):
	#align the correct order of english words for the de sentence
	en_words = en_sentence.split()
	de_words = de_sentence.split()
	l = len(en_words)
	m = len(de_words)
	alignment = []
	#iterate through all the german words first
	i = 1
	for de_word in de_words:
		max_t = 0.0
		arg_max_alignment = 0
		#initialize the max_t with the NULL condition
		if de_word in en_dict["NULL"]:
			max_t = en_dict["NULL"][de_word] * q[(i,l,m)][0]
		#else:
			#if the de_word can not be translated into NULL, it can not use position 0
			#max_t = 1
		#use the en_cur_position variable to record the position of english sentence	
		en_cur_position = 1
		for en_word in en_words:
			if de_word in en_dict[en_word]:
				temp_prob = en_dict[en_word][de_word] * q[(i,l,m)][en_cur_position]
			if temp_prob > max_t:
				max_t = temp_prob
				arg_max_alignment = en_cur_position
			en_cur_position += 1

		alignment.append(arg_max_alignment)
		i += 1
	return alignment

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2])

