
import argparse
import codecs
import sys
from rewrite import edit_distance, rewrite_string


def make_instances(item, tags, right=5, left=5, sep=','):
    """
    Convert a item into a windowed representation as described in
    Van den Bosch and Daelemans (1999):

    Args:
        - item (str): a string representing a word
        - tags (list): a list of tags per character of ITEM
        - right (int): context on the right side of a focus letter.
        - left (int): context on the left side of a focus letter.
        - sep (str): the separator used to separate variables in the window.
    Yields:
        a window per character of item

    """
    for i in xrange(len(item)):
        inst = []
        for j in xrange(i, i + 1 + right + left):
            if j < left or j >= len(item) + left:
                inst.append('_')
            else:
                # if the item contains elements that are the same
                # as 'sep', choose another symbol ('C')
                if item[j-left] == sep:
                    inst.append('C')
                else:
                    inst.append(item[j-left])
        inst.append(tags[i])
        yield sep.join(inst)


def format_testitem(item, size=5, sep=','):
    """
    Create a window with empty outcome slots ('?') for a test item::

        >>> for window in format_testitem('aardigheidje'):
        ...     print window
        _,_,_,_,_,a,a,r,d,i,g,?
        _,_,_,_,a,a,r,d,i,g,h,?
        _,_,_,a,a,r,d,i,g,h,e,?
        _,_,a,a,r,d,i,g,h,e,i,?
        _,a,a,r,d,i,g,h,e,i,d,?
        a,a,r,d,i,g,h,e,i,d,j,?
        a,r,d,i,g,h,e,i,d,j,e,?
        r,d,i,g,h,e,i,d,j,e,_,?
        d,i,g,h,e,i,d,j,e,_,_,?
        i,g,h,e,i,d,j,e,_,_,_,?
        g,h,e,i,d,j,e,_,_,_,_,?
        h,e,i,d,j,e,_,_,_,_,_,?

    Args:
        - item (str): a string representing a word
        - sep (str): the separator used to separate variables in the window.
    Yields:
        a complete window for word in which all outcomes are marked as '?'
    """
    return make_instances(item, '?'*len(item), left=size, right=size, sep=sep)


def make_tagged_instances(inst, fn, size=5, sep='+', tagsep='@', windowsep=','):
    """
    Create a window for a word with the given tags::

        >>> for window in make_tagged_instances('gezellig@A+heid@N|A*', get_tags):
        ...     print window
        _,_,_,_,_,g,e,z,e,l,l,A
        _,_,_,_,g,e,z,e,l,l,i,0
        _,_,_,g,e,z,e,l,l,i,g,0
        _,_,g,e,z,e,l,l,i,g,h,0
        _,g,e,z,e,l,l,i,g,h,e,0
        g,e,z,e,l,l,i,g,h,e,i,0
        e,z,e,l,l,i,g,h,e,i,d,0
        z,e,l,l,i,g,h,e,i,d,_,0
        e,l,l,i,g,h,e,i,d,_,_,N|A*
        l,l,i,g,h,e,i,d,_,_,_,0
        l,i,g,h,e,i,d,_,_,_,_,0
        i,g,h,e,i,d,_,_,_,_,_,0

    Args:
        - inst (str): a string with morphemes separated by SEP holding tags
            separated by TAGSEP.
        - fn (function): the function used to extract the tags or segments.
            Use :func:`get_segments` to create an instance with segmentation
            marks. Use :func:`get_tags` to create an instance with Part of
            Speech marks.
        - size (int): the window size
        - sep (str): the separator used to separate the items of inst
        - tagsep (str): the separator used to separate tags from
        - windowsep (str): the separator used to separate variables in the window.
    Yields:
        a complete window for word in which all outcomes are marked as '?'
    """
    word, tags = fn(inst, sep=sep, tagsep=tagsep)
    if len(word) != len(tags):
        raise ValueError("Window has a different size than tags...")
    tags = [tag.replace('.', '*') for tag in tags]
    return make_instances(word, tags, right=size, left=size, sep=windowsep)


def get_rewrite_tags(inst, sep=None, tagsep=None, default='0'):
    """
    Return the original word and the rewite tags to transform the
    word into the corresponding lemma per character of word. An instance
    such as ``k,l,o,p,p+DEL:p,e,n`` is converted into::
    
        ('kloppen', ['0','0','0','0','DEL:p','0','0'])
    """
    word, tags = [], []
    for elt in inst.split(','):
        if len(elt.split('+')) > 1:
            tags.append('+'.join(elt.split('+')[1:]))
        elif tagsep in elt:
            tags.append(elt[2:])
        else:
            tags.append(default)
        word.append(elt[0])
    return word, tags


def transform(word, target):
    for instance in make_tagged_instances(
        ','.join(rewrite_string(edit_distance(word, target).backtrace())), get_rewrite_tags):
        yield instance

def main():
    parser = argparse.ArgumentParser(
        prog='train',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-f', dest = 'file', type = str,
        required=True, help = 'path pointing to phonology lexicon')
    parser.add_argument(
        '-o', dest = 'output', type = argparse.FileType('w'),
        required = False, default = sys.stdout)
    args = parser.parse_args()
    for line in codecs.open(args.file, encoding='utf-8'):
        line = line.split('\\')
        if len(line) < 16: continue
        ortography, phonology = line[8], line[15]
        print ortography, phonology
        for instance in transform(ortography, phonology):
            try:
                args.output.write(u'{}\n'.format(instance).encode('utf-8'))
            except UnicodeDecodeError:
                print 'Error parsing', (ortography, phonology)
    args.output.close()


if __name__ == '__main__':
    main()
