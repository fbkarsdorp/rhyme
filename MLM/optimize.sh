#! /usr/bin/bash

NGRAM_COUNT='/Users/folgert/Downloads/srilm/bin/macosx/ngram-count'
for n in 3 4 5 6 7 8 9
do
	$NGRAM_COUNT -text $1 -order $n -lm $1.$n.lm -wbdiscount2 -wbdiscount3 -wbdiscount4 -wbdiscount5
done
NGRAM='/Users/folgert/Downloads/srilm/bin/macosx/ngram'
for n in 3 4 5 6 7 8 9
do
	echo "Computing perplexity with max n=$n"
	$NGRAM -ppl $2 -order $n -lm $1.$n.lm
done