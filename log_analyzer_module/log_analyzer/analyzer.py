from __future__ import print_function
import os
import re
import pickle
from collections import Counter, OrderedDict

filepath = os.path.dirname(os.path.abspath(__file__))
os.environ["NLTK_DATA"] = os.path.join(filepath, "nltk_data")

from nltk import word_tokenize, NaiveBayesClassifier
# from lib.nltk.classify.scikitlearn import SklearnClassifier
# from lib.sklearn.naive_bayes import MultinomialNB, BernoulliNB
# from nltk.tokenize import *
# from nltk import pos_tag
# from nltk.text import Text


__word_features__ ={
    'conflict'      : 0.7,        'conflicting'   : 0.7,          'fail': 0.8,                'failed': 0.8,
    'pointless'     : 0.2,        'variable'      : 0.1,          'fatal':1,                  'failure': 0.8,
    'abnormal'      : 0.8,        'redefinition'  : 0.8,          'death': 0.3,               'void':0.4,
    'abend'         : 0.8,        'uninitialized' : 0.8,          'implicitly':0.1,           'invalid':0.6,
    'overflowed'    : 0.8,        'identifier'    : 0.1,          'declared': 0.1,            'eof':0.3,
    'unexpected'    : 0.6,        'reference'     : 0.3,          'wrong': 0.6,               'region': 0.01,
    'critical'      : 0.6,        'denied'        : 0.6,          'type': 0.1,                'implicit':0.8,
    'unresolved'    : 0.8,        'indent'        : 0.1,          'fault':0.9,                'protection':0.1,
    'illegal'       : 0.5,        'unterminated'  : 0.4,          'undeclared':0.7,           'abort':0.9,
    'unrecoverable' : 0.6,        'underflow'     : 0.8,          'unknown':0.9,              'assert':0.8,
    'duplicate'     : 0.7,        'overflow'      : 0.8,          'timeout':0.5,              'intermittent':0.1,
    'mismatch'      : 0.8,        'declaration'   : 0.1,          'exception':0.9,            'recoverable':0.1,
    'undefined'     : 0.8,        'cast'          : 0.1,          'without':0.1,              'constant':0.1,
    'exclude'       :-1,          'ok'            :  -1,          'ignored': -1,              'not': 0.1,
    'unable'        : 0.4,        'cannot'        : 0.1,          'recipe' : 0.1,             'constant': 0.1,
    'referenced '   : 0.1,        'out'           : 0.1,          'no'     : 0.2,             'such':  0.1,
    'uncompleted'   : 0.1,        'macro'         :0.1,           'unsed'   :0.2,             'expire': 0.1,
    'redefined'     : 0.5,        'unreachable'   : 0.2,
}




class Analyzer:
    INFO = {0: 'PASS', 1:'Error'}
    FILE_PATH = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
    PUNCTUATION = ['[' , ']', ':', '\'', '"', '-',
        ',', '.', '"', '(', ')', 'of', 'the', '`', '``', '#', '>', '<', "''",
        '--', '/b', '/', '\\\\', '=', '==', "!"]
    @staticmethod
    def load( filepath):
        context = open(filepath, encoding="utf-8", errors="replace").read().split("\n")
        return context

    def __init__(self):
        # with file(self.FILE_PATH+'/negative.pkl', 'rb') as f:
        #     self.negative_words = pickle.load(f)
        self.phrases       = self.load(self.FILE_PATH + '/_data/phrases.txt')
        self.stopwords     = self.load(self.FILE_PATH + '/_data/stopwords.txt')

        self.stopwords.extend(self.PUNCTUATION)
        try:
            self.classifier    = self.load_classifier()
        except IOError:
            pass
        self.word_pattern = re.compile(r'^[a-z]{2,}$', re.I)
        self.words = []
        sub_regular = [
            r"(\d){4}(-\d\d){2}.*\d\d:\d\d:\d\d",
            r"(c:[\\\\/])([-_\.\w\s\(\)]+?[\\\\/]){2,}",
            r"^\s+",
            # "^\w+[\w_]+\.\w{1,5}[\s\d:,\[\]\(\)]*",
        ]
        self.subpatterns = [re.compile(sr, re.I) for sr in sub_regular]
        # try:
        #     with open(self.FILE_PATH+'/_data/wordfreq.pkl', 'rb') as fileobj:
        #         self.keywords = set(pickle.load(fileobj).keys())
        #         self.keywords.update(set(__word_features__.keys()))
        #         # print self.keywords
        #         # self.default_features = {k:False for k in self.keywords}
        # except IOError:
        #     pass
        # except Exception as e:
        #     raise e

    def pre_tokenize(self, raw_text):
        tokens = word_tokenize(raw_text)
        tokens = [w.lower() for w in tokens if w not in self.stopwords and self.word_pattern.match(w)]
        return tokens

    def compute_wordfreq(self, raw_text):
        raw_text = brief_text(raw_text.lower(), self.subpatterns)
        document_words = self.pre_tokenize(raw_text)
        for word in document_words:
            if self.word_pattern.match(word) is not None:
                self.words.append(word)

    def save_wordfreq(self):
        print("Words count: %s"%len(self.words))
        counter = Counter(self.words)
        data = dict(counter)
        cnt = float(len(self.words))
        new_data = dict()

        for k,v in data.items():
            new_data[k] = v

        self.keywords = new_data.keys()
        print("Features count: %s"%len(self.keywords))
        new_data = OrderedDict(sorted(new_data.items(), key=lambda d:d[1], reverse = True))
        # print new_data
        f = open('_data/wordfreq.pkl', 'wb')
        pickle.dump(new_data, f, 3)
        f.close()

    def get_features(self, raw_text, debug=False):
        raw_text = brief_text(raw_text.lower(), self.subpatterns)
        features = {word: 0 for word in __word_features__}
        features['error'] = 0
        features['errors'] = 0
        features['warnings'] = 0
        features["warning"] = 0
        features['fail'] = 0
        features['fatal'] = 0
        features['exception'] = 0

        if "error(s)" in raw_text:
            features['error(s)'] = 1

        document_words = self.pre_tokenize(raw_text)
        if debug:
            print(raw_text)
            print(document_words)

        for word in document_words:
            features[word] = 1

        if debug:
            print("Features: %s"%features)

        # print features
        return features


    def train_classifier(self, directory=None):
        #load noerror sample
        print("Loading Training Data...")
        documents = list()
        falseset = list()
        passset = list()

        if directory:
            err_path = directory + "/error/"
            files = os.listdir(err_path)
            for fname in files:
                all_lines = Analyzer.load(err_path+fname)
                temp = [(line, True) for line in all_lines if line.strip() ]
                falseset.extend(temp)
                if "phrases" in fname:
                    for ti in range(80):
                        falseset.extend(temp)

            pass_path = directory + "/pass/"
            files = os.listdir(pass_path)
            for fname in files:
                all_lines = Analyzer.load(pass_path+fname)
                temp = [(line, False) for line in all_lines if line.strip()]
                passset.extend(temp)
                # if "abspass" in fname:
                #     for ti in range(10):
                #         passset.extend(temp)

        else:
            all_lines = Analyzer.load(self.FILE_PATH + "/samples/pass.txt")
            passset = [(line, False) for line in all_lines]

            #load error sample
            all_lines = Analyzer.load(self.FILE_PATH + "/samples/error.txt")
            falseset = [(line, True) for line in all_lines]

        documents.extend(falseset)
        documents.extend(passset)

        print("Data Size: %s"%len(documents))
        print("False sample: %s"%len(falseset))
        print("Pass sample: %s"%len(passset))

        # print("Compute Key Word Freq...")
        # [self.compute_wordfreq(d) for (d,c) in documents]
        # self.save_wordfreq()

        print("Feature Data.. ")

        featuresets = [(self.get_features(d), c) for (d,c) in documents]
        print("Training...")
        #self.classifier = SklearnClassifier(BernoulliNB()).train(featuresets)
        self.classifier = NaiveBayesClassifier.train(featuresets)

        f = open("classifier","wb")
        pickle.dump(self.classifier, f, 3)
        f.close()

    def load_classifier(self):
        f = open(self.FILE_PATH+"/classifier","rb")
        classifier = pickle.load(f)
        f.close()
        return classifier

    def inspect(self, filepath):
        result = list()
        context = Analyzer.load(filepath)

        for c, each_line in enumerate(context):
            if each_line.strip():
                dist = self.classifier.prob_classify(self.get_features(each_line, debug=False))
                if dist.max():
                    result.append((c, each_line, dist.prob(True)))

        return result

    def inspect_text(self, text, debug=False):
        features = self.get_features(text, debug)
        if debug:
            # print self.classifier.most_informative_features(n=3)
            for k,v in features.items():
                if v == 1:
                    print(k)

        return self.classifier.prob_classify(features)

    def get_confidence(self, raw_text, prob):
        raw_text = raw_text.lower()
        document_words = self.pre_tokenize(raw_text)
        for p in self.phrases:
            if p in raw_text:
                phrase = 1
                break
        else: phrase = 0
        ws = 1 if len(document_words) > 1 else -1
        return phrase*2 + prob*ws

    def inspect_main(self, filepath, type="auto", brief=True):
        def _get_the_max(info):
            confidencelist = list()
            for (index, (num, text, prob)) in enumerate(info):
                con = self.get_confidence(text, prob) - index*0.00001
                confidencelist.append((con, num, text))
            maxcondition = sorted(confidencelist, key=lambda t: t[0])[-1]
            if brief:
                return (maxcondition[1], brief_text(maxcondition[2], self.subpatterns))
            else:
                return maxcondition

        match_info = self.inspect(filepath)

        if match_info:
            ignored_text = self.load(self.FILE_PATH + '/_data/ignore')
            match_info = [item for item in match_info if item not in ignored_text]
            error_info = [item for item in match_info if 'error' in item[1].lower() or 'exception' in item[1].lower()]
            if error_info:
               return _get_the_max(error_info)
            else:
                return _get_the_max(match_info)
        else:
            return None, None

    def word_freq(self):
        counter = Counter(self.words)
        print(counter.most_common(100))

def brief_text(raw_text, patterns):
    for pa in patterns:
        raw_text = pa.sub("", raw_text)
    return re.compile(r"\s+").sub(" ", raw_text)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Selen Tool.',)
    parser.add_argument('-s', '--string', help='predict string')
    parser.add_argument('-d', '--demo', action='store_true', help='run demo')
    parser.add_argument('-t', '--train', action='store_true', help='specify the local installer')
    parser.add_argument('-f', '--feature', action='store_true', help='show most informative features')
    parser.add_argument('-a', '--analysis', action='store_true', help='analysis string')
    parser.add_argument('-p', '--path',  help='file path')
    parser.add_argument('--test', action='store_true', help='test')
    args = parser.parse_args()

    s = Analyzer()
    if args.train:
        s.train_classifier(r"C:\clogs")

    if args.feature:
        print(s.classifier.labels())
        s.classifier.show_most_informative_features(150)
    # s.word_freq()

    if args.demo:
        os.system("python {0}/test_sample.py".format(filepath))

    if args.string:
        print(s.inspect_text(args.string, True).prob(True))

    if args.path:
        match_info = s.inspect(args.path)
        for (index, (num, text, prob)) in enumerate(match_info):
            print(prob, num, text)

    if args.test:
         os.system("python {0}/sample_test2.py".format(filepath))
