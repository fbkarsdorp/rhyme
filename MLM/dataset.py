
import argparse
import os

from itertools import groupby
from sklearn.cross_validation import train_test_split


parser = argparse.ArgumentParser(description="Evaluate and optimize LM for melodies.")
parser.add_argument("-f", "--file", dest="file", required=True)
parser.add_argument("-s", "--split", dest="split", default=0.2, type=float)
parser.add_argument("-r", "--random-seed", dest="seed", default=None, type=int)
args = parser.parse_args()

melodies = [list(melody) for _, melody in groupby(open(args.file), lambda l: l.split('#')[1].split(',')[0])]
train, test = train_test_split(melodies, test_size=args.split, random_state=args.seed)

for name, dataset in (('train', train), ('test', test)):
	with open(args.file + ".%s" % name, 'w') as out:
		out.write('\n'.join(phrase.strip().split('#')[0] for melody in dataset for phrase in melody))

