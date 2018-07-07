import re
import os
import itertools
from simhash import Simhash
from simhash import SimhashIndex
from partition import *


class FindSimilar:
    f = 64
    dic = {}
    idx = SimhashIndex({}, f=f)

    def __init__(self, txtfile):
        id_, hs = self.get_sim(txtfile)

    def get_sim(self, doc):
        with open(doc, 'r') as fr:
            cont = fr.read()
        hs = Simhash([ele for ele in re.split('/|\n+', cont) if ele])
        docid = os.path.split(doc)[1].rstrip('.txt')
        FindSimilar.dic[docid] = hs
        FindSimilar.idx.add(docid, hs)
        return docid, hs

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
                if dis <= 3:
                    dis_pair = dis, set(ele)
                    dups.append(dis_pair)
        return dups

    def get_duplicates(self, pathsub):
        duplicates = []
        docs = os.listdir(pathsub)
        for doc in docs:
            ls = self.get_dup(*self.get_sim(pathsub + doc))
            if ls:
                duplicates.extend([ele for ele in ls if ele not in duplicates])

        return duplicates