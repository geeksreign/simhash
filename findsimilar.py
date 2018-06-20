import re
import os
import itertools
from simhash import Simhash
from simhash import SimhashIndex
from partofspeech import *

pathfrom = '/home/yy/usstock/usstockresearch/'
pathsub = '/home/yy/usstock/usstockcut/'


class FindSimilar:
    k = 3
    f = 64
    dic = {}
    idx = SimhashIndex({}, k=k, f=f)

    def __init__(self, pathsub=pathsub):
        self.pathsub = pathsub

    def get_sim(self, doc):
        with open(doc, 'r') as fr:
            cont = fr.read()
        hs = Simhash([ele for ele in re.split('/|\n+', cont) if ele])
        FindSimilar.dic[doc] = hs
        FindSimilar.idx.add(doc, hs)
        return doc, hs

    def get_dup(self, doc, hs=None):
        dups = []
        if not hs:
            dup = FindSimilar.idx.get_near_dups(self.get_sim(doc)[1])
        else:
            dup = FindSimilar.idx.get_near_dups(hs)
        if len(dup) >= 2:
            pair = itertools.combinations(dup, 2)
            for ele in pair:
                dis = self.dic[ele[0]].distance(self.dic[ele[1]])
                dis_pair = dis, set(ele)
                dups.append(dis_pair)
        return dups

    def get_duplicates(self):
        duplicates = []
        docs = os.listdir(self.pathsub)
        for doc in docs:
            ls = self.get_dup(*self.get_sim(self.pathsub + doc))
            if ls:
                duplicates.extend([ele for ele in ls if ele not in duplicates])

        return duplicates

if __name__ == '__main__':
    PartofSpeech(pathfrom, pathsub)
    txtfile = None
    dups = FindSimilar(pathsub)
    if not txtfile:
        sim = dups.get_duplicates()
    else:
        sim = dups.get_dup(txtfile)
