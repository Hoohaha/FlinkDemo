
import re
import os
from collections import Counter
import difflib
from pprint import pprint
import copy


N = 0
PATTERNs = [
    re.compile("^\w+[\w_\d]+\.\w[\d:\(\)\w]* "),
    re.compile("^(?:[a-zA-Z]\:|\\\\[\w\.]+\\[\w.$]+).*\\\\")
]

def refactor_string(string):
    '''
    remove "\n"
    remove xxxx.h
    '''
    string = string.replace("\n", "")
    if len(string) > 30:
        for ptr in PATTERNs:
            string = ptr.sub("", string)
    return string

def get_matches(string, prob):
    '''
    string: type: str,
    prob: type: list, search in prob list
    return a list which contain the similarity item.
    '''
    matches = list()
    for p in prob:
        ratio = difflib.SequenceMatcher(None, string, p).ratio()
        if ratio >= 0.5:
            matches.append(p)
    return matches


def _compute(dataset):
    '''
    compute the similarity.
    '''
    global N
    N += 1
    category = dataset.keys()
    print("iter: %sst"%N)
    print("current category size: %s\n"%len(category))

    for index in range(len(category)):
        key = category[index]
        c = copy.deepcopy(category)
        del c[index]

        matches = get_matches(key, c)
        if matches:
            for mat in matches:
                dataset[key][0] += dataset[mat][0]
                dataset[key][1].extend(dataset[mat][1])
                del dataset[mat]
            return _compute(dataset)
    else:
        return dataset




def log_cluster(data):
    '''
    data: type list
    return a dict
    '''
    print("data size: %s"%len(data))
    data = [refactor_string(d) for d in data]
    counter = Counter(data)
    dataset = {k:[counter[k], [k]] for k in counter}
    dataset = _compute(dataset)
    print("after cluster size: %s" % len(dataset))
    return dataset


def test():
    import time
    time0 = time.time()
    with open("C:/clogs/er.txt", 'r') as fileobj:
        data = fileobj.readlines()
        pprint(log_cluster(data))
    t = time.time()-time0
    if t > 60:
        print("Finished in: %.1f(min)"%(t/60.0))
    else:
        print("Finished in: %f(s)" % t)

if __name__ == '__main__':
    test()