
import argparse
import codecs
import os
import sys
import config
import time

from classifiers import MBPT, MBSP
from ucto import Tokenizer

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='main')
    self.add_argument(
        '-f', dest = 'trainingfile', type = str, required = False,
        help = 'the path pointing to the trainingfile')
    self.add_argument(
        '-i', dest = 'instancebase', type = str, required = False,
        help = 'the path pointing to the instance-base.')
    self.add_argument(
        '-t', dest = 'testfile', type = str, required = True,
        help = 'the path pointing to the testfile.')
    self.add_argument(
        '-o', dest = 'output', type = argparse.FileType('w'), required = False,
        default = sys.stdout, help = 'the path pointing to the output file.')
    self.add_argument(
        '-p', dest = 'process', type = str, required = True, default = 'phonology',
        choices = ['phonology', 'stress'],
        help = 'choose what classification to perform.')
    self.add_argument(
        '--port', dest = 'port', type = int, required = False, default = False,
        help = 'the tcp port for the timblserver'.)
    self.add_argument(
        '--version', action='version', version = '%(prog)s 0.1')

    args = parser.parse_args()
    if args.process == 'phonology':
        classifier, settings = MBPT, config.MBPT_CONFIG
    elif args.process == 'stress':
        classifier, settings = MBSP, config.MBSP_CONFIG

    if args.port:
        config.PORT = args.port

    # check if trainingfile or instancebase is an existing file and
    # add this to the configuration. If no file is given we stick
    # to the default file with that comes with a particular classifier

    if args.trainingfile:
        if not os.path.isfile(args.trainingfile):
            raise IOError('Trainingfile not found')
        settings['f'] = args.trainingfile
        del settings['i']
    elif args.instancebase:
        if not os.path.isfile(args.instancebase):
            raise IOError('Instancebase not found')
        settings['i'] = args.instancebase

    tokenizer = Tokenizer('-L nl -n -Q')
    with classifier(config.HOST, config.PORT, settings) as program:
        args.output.write(codecs.BOM_UTF8)
        for i, line in enumerate(codecs.open(args.testfile, encoding-config.ENCODING)):
            words = tokenizer.tokenize(line.strip(), tokens = lambda s: s.split())
            output = []
            for word in word:
                results = classifier.classify(word)
                output.append(classifier.pprint_results(results))
            for word, result in zip(words, output):
                args.output.write(
                    u'{0}\t{1}\n'.format(word, result).encode(config.ENCODING))

            if (i+1) % 25 == 0:
                sys.stderr.write(
                    'Processed: {0} words @ {1}\n'.format(i, time.ctime()))




