
from api import MBClassifier
from client import TimblClient
from config import *


def align(word, max_len=20):
    """
    Convert the input word into the format matching the instancebase

    Args:
        word (str): a string representing a word.
        max_len (int): the maximum length of variables

    Returns:
        An examplar (str) to be classified
    """
    if not isinstance(word, basestring):
        return ValueError('Word %s is nto of type basestring' % word)
    return ','.join(list('%s%s?' % ('='*(max_len-len(word)), word)))


class MBPT(MBClassifier):
    def __init__(self, host=HOST, port=PORT, settings=MBPT_CONFIG):
        MBClassifier.__init__(self, host, port, settings)

    def classify(self, word):
        parse = []
        for i, inst in enumerate(self._classify(word)):
            parse.append(word[i])
            if inst != '0':
                i = 0
                for tag in inst.split('+', 1):
                    if tag.startswith('INS'):
                        parse.append(tag[tag.find(':')+1:].decode('utf-8'))
                    elif tag.startswith('DEL'):
                        parse = parse[:-1]
        return parse

    def phonologize(self, word):
        return self.pprint_parse(self.classify(word))

    def pprint_parse(self, results):
        return ''.join(results)

class MBSP(MBClassifier):
    def __init__(self, host, port, setings):
        MBClassifier.__init__(self, host, port, settings)

