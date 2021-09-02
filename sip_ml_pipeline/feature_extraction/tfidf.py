# taken from https://github.com/mr-ma/sip-ml/blob/master/ml-scripts/tfidf.py


import functools
import os
import random
import re
import string

import numpy
import pandas as pd
from gensim.corpora import dictionary
from sklearn.feature_extraction.text import TfidfTransformer
from tabulate import tabulate


class MyCorpus(object):
    """ Helper class for the gensim-based TF-IDF extraction """

    def randomString(self, stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def clean_IR(self, block):
        # remove volatile, unreachable and alignments
        block = block.replace('volatile', '').replace('unreachable', '').replace('(align)(\s)(\d+)', '').replace(
            '(align)(\d+)', '').replace('icmp', self.randomString())

        # fix aligns
        block = block.replace('align ', 'align')
        # clean metadata flags
        block = re.sub(r'(,)(\s+)(!)((?:[a-z][a-z0-9_]*))', "", block)
        block = re.sub(r'(!)(\d+)', "", block)
        # before = len(block)
        # block = re.sub(r'(store i32 5555*)','',block)
        # block = re.sub(r'(store i32 4444*)','',block)
        # after = len(block)
        # if before > after:
        # clean comma at the end of each line
        # block = re.sub(r'(,)(\s)(\|)(\.)(\|)','|.|',block)
        # block = re.sub(r'(,)(\|)(\.)(\|)','|.|',block)
        # replace %n with VAR
        block = re.sub(r"(%)(\d+)", "VARo", block)
        block = re.sub(r"(%)(_\d+)", "VARo", block)
        # replace %varname with namedVar
        block = re.sub(r'(%)((?:[a-z][a-z0-9_\.]*))', "VARo", block)
        block = re.sub(r'(%)(.)((?:[a-z_][a-z0-9_\.]*))', "VARo", block)

        # replace %n with REF
        block = re.sub(r"(@)(\d+)", "REFo", block)
        # replace %varname with namedVar
        block = re.sub(r'(@)((?:[a-z][a-z0-9_\.]*))', "REFo", block)
        block = re.sub(r'(@)(.)((?:[a-z_][a-z0-9_\.]*))', "REFo", block)

        # block = re.sub(r"-?(\d+)", "KONSTANT", block)

        # replace llvm native functions
        block = re.sub(r'(call)(\s)(void)(\s)(@llvm.).*?(\|)(\.)(\|)', ' |.|',
                       block)  # (\.)*?(\|)(\.)(\|)','|.|',block)
        # replace int pointers
        # block = re.sub(r'(i8)', "io", block)
        # block = re.sub(r'(i16)', "ih", block)
        # block = re.sub(r'(i32)', "itt", block)
        # block = re.sub(r'(i64)', "iss", block)

        # clean #numbers
        block = re.sub(r'0[xX][0-9a-fA-F]+', 'hexval', block)
        block = re.sub(r'0[xX][k0-9a-fA-F]+', 'hextag', block)
        block = re.sub(r'(#)(\d+)', "#n", block)
        # replace %n with VAR
        # block = re.sub(r'(,)(\s+)', "narg", block)
        # block = re.sub(r'(;)', " ", block)
        # replace int values
        block = re.sub(r"[+\-]?[^\w]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)", "KE", block)
        # block = re.sub(r"-?[\d.]+(?:e-?\d+)?", "KE", block)
        block = re.sub(r'([\s[;(^-])(\d+)([ \)\];,$])', r'\1N\3', block)
        block = re.sub(r'(\s+)(\d+)(\s+)', " N ", block)
        block = re.sub(r'(\s+)(\d+)(\))', " N) ", block)
        block = re.sub(r'(\s+)(\d+)(,)', " N,", block)
        block = re.sub(r'(\s+)(-)(\d+)(\s+)', "-N ", block)
        block = re.sub(r'(\s+)(-)(\d+)(,)', "-N", block)
        block = re.sub(r'(\b-\d+\b)', "-N", block)
        block = re.sub(r'(\b\d+\b)', "N", block)
        return block

    def dump_tokens(x, y):
        x.tokens.add_documents([y])

    def get_tokens(x, y):
        if not isinstance(y, str):
            print('size', x.dataframe.size)
            print(tabulate(x.dataframe, headers='keys', tablefmt='psql'))
            print(y)
            exit(1)

        unclean_y = y  # .split('|.|')
        y = x.clean_IR(y.lower())
        clean_y = y  # .split('|.|')
        z = zip(clean_y, unclean_y)
        # for ci,ui in z:
        # print("From\n", ui, '\nTo:\n', ci, '\n')
        # print("**********************")
        # print(unclean_y.replace('|.|','\n'),'##############\n',clean_y.replace('|.|','\n'),'************')
        a = [word for word in y.replace("|.|", '\n').split() if
             word not in ['', ' ', ",", "%", "(", ")", ",", ":", "\n", "$", "|.|"]]
        return a

    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.tokens = dictionary.Dictionary()
        # Retrieve tokens form documents, populating the tokens dictionary
        self.dataframe = self.dataframe.apply(self.get_tokens)
        # print(tabulate(self.dataframe, headers='keys', tablefmt='psql'))
        # print(self.dataframe)
        self.dataframe.apply(self.dump_tokens)
        # self.tokens.add_documents(content)

    def __iter__(self):
        # Iterate over documents in the corpus retrurning their token counts
        for index, doc in self.dataframe.iteritems():
            yield self.tokens.doc2bow(doc)


def cmpTuple(x, y):
    #    if type(x) != tuple or type(y) != tuple or not len(x) == len(y) == 2:
    #        return 0
    if x[1] > y[1]:
        return -1
    elif x[1] < y[1]:
        return 1
    else:
        return 0


def getTupleKey(l, k):
    if len(l) < 1:
        return 0
    for element in l:
        if type(element) == tuple and len(element) == 2:
            if element[0] == k:
                return element[1]
    return 0


def extract_tf_idf_memory_friendly(df, maxfeatures=128, data_path='', tokenextension="token", outextension="tfidf"):
    corpus_mem_friendly = MyCorpus(df)
    # Save the tokens to file and load them again just to get the cross-document count (:s)
    filename = "corpus.%s" % (tokenextension)
    corpus_mem_friendly.tokens.save_as_text(os.path.join(data_path, filename))
    # print("Saved", filename)
    tokens = open(os.path.join(data_path, filename)).read().split('\n')
    tokenTuples = []
    for t in tokens:
        # print(t)
        if len(t) > 1 and len(t.split('\t')) > 2:
            tokenTuples.append((int(t.split('\t')[0]), int(t.split('\t')[2])))
    # Now sort them descendingly
    # print tokenTuples #TODO: Remove me!!
    tokenTuples.sort(key=functools.cmp_to_key(cmpTuple))
    # exit(1)
    # print(tokenTuples)

    # Build a list of vectors
    allVectors = [v for v in corpus_mem_friendly]

    # Build a numpy matrix of zeros
    # X = numpy.zeros((df.count(), maxfeatures))
    X = numpy.zeros((len(allVectors), min(len(tokenTuples), maxfeatures)))
    # print('X', len(X), len(X[0]))
    # print('Vector', len(allVectors), min(len(tokenTuples), maxfeatures))
    # Go over the first [maxfeatures] of the tokenTuples and populate the matrix
    # prettyPrint("Picking the best %s features from the sorted tokens list" % maxfeatures)

    for vectorIndex in range(len(allVectors)):
        for featureIndex in range(min(len(tokenTuples), maxfeatures)):
            # a. Get the token key
            tokenKey = tokenTuples[featureIndex][0]
            a = getTupleKey(allVectors[vectorIndex], tokenKey)
            X[vectorIndex][featureIndex] = a


    # Now apply the TF-IDF transformation
    optimusPrime = TfidfTransformer()
    X_tfidf = optimusPrime.fit_transform(X)
    return pd.DataFrame(X_tfidf.todense())
