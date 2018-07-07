import os
import re
import sys
import jieba
from langconv import *

#sys.version_info
#sys.getdefaultencoding()
#reload(sys)
#sys.setdefaultencoding('utf-8')
#jieba.load_userdict(mydic)

testpath = '/home/abc/trial_for_dup/usstock/REPORT/'
initpath = '/home/abc/trial_for_dup/usstock/usstockresearch/'
stopws = '/home/abc/trial_for_dup/stop_words_v0520.txt'
mydic = '/home/abc/trial_for_dup/abcChinesebeta.txt'
cmchinese = '/home/abc/trial_for_dup/commonchinese.txt'

models = [
         '\n分析师声明.+\n',
         '本报告署名分析师在此声明.+\n',
         '\n公司业绩点评报告.+\n',
         '\n披露声明.+\n',
         '\n分析师申明.+\n',
         '\n行业投资评级说明.+\n',
         '\n分析师承诺.+\n',
          '\n投资评级定义.+\n',
         '\n投资评级说明.+\n',
         '\n行业及公司评级.+\n',
          '\n评级标准.+\n',
          '\n免责声明及披露.+\n',
         '\n.{0,2}免责声明.+\n']


class Partition:
    _initial = 0
    _stopws = ''
    _cmchinese = ''

    def __init__(self, doc, stopws=stopws, mydic=mydic, cmchinese=cmchinese):
        """ param doc is the document to be cut, and doc must be a txt file with complete path."""
        self.doc = doc
        if Partition._initial == 0:
            jieba.load_userdict(mydic)
            Partition._stopws = Partition._getstp(stopws)
            Partition._cmchinese = Partition._get_char_list(cmchinese)
        Partition._initial += 1

        if self.doc.endswith('.txt') and os.path.getsize(self.doc):
            self.pathfrom = os.path.split(self.doc)[0]
            self.pathto = self.pathfrom[:self.pathfrom.rfind('/') + 1] + 'part/'
            self.pathfrom += '/'
            if not os.path.exists(self.pathto):
                os.mkdir(self.pathto)
            self._parttofile(os.path.split(self.doc)[1])

    @staticmethod
    def _getstp(stopws):
        """obtain stop words from file"""
        with open(stopws, 'r') as rs:
            stpws = rs.read()
        return stpws

    @staticmethod
    def _is_chinese(uchar):
        """check if uchar is a chinese character"""
        return all([True if ele >= u'\u4e00' and ele <= u'\u9fa5' else False for ele in uchar])

    def _preprocess(self, f):
        fils = []
        nul = re.compile(r'\s{5,}')
        rule = re.compile(r'(\d+?.?\d*%?\s+)+')
        mode = re.compile('|'.join(models), flags=re.S)
        with open(self.pathfrom + f, 'r') as frt:
            cont = frt.read()
            cl = mode.sub('', cont)

        sentgen = (ele for ele in cl.split('\n') + ['\n'] if ele)
        fline = next(sentgen)

        while fline != '\n':
            if not re.search(nul, fline) and not re.search(rule, fline):
                if not re.search('，|。', fline):
                    fils.append(fline.strip())
                    fline = next(sentgen)
                    continue
                incmp = fline
                while fline != '\n' and not fline.rstrip().endswith('。'):
                    fline = next(sentgen)
                    incmp += fline.rstrip()
                fils.append(incmp.strip())
            try:
                fline = next(sentgen)
            except StopIteration:
                break
        return fils

    def _partition(self, corpsch):
        cuted = []
        for sent in corpsch:
            sent = re.sub(r'\s|\W|[a-z]|[A-Z]', '', sent)
            if sent:
                sent = Converter('zh-hans').convert(sent)  # # traditinal chinese transfromation
                segs = jieba.cut(sent)
                cutsent = '/'.join(ele for ele in segs if self._is_chinese(ele) and ele
                                   not in self._stopws)
                cuted.append(cutsent)
        return cuted

    def _parttofile(self, f):
        relf = self.pathto  + f
        cleaned = self._preprocess(f)
        with open(relf, 'w+') as fw:
            for cutf in self._partition(cleaned):
                fw.write(cutf + '\n')

        apd = False
        with open(relf, 'r') as fr:
            cont = fr.read(1000)
            if not cont.strip():
                apd = True
            else:
                slash = 0
                for char in cont:
                    if char == '/':
                        slash += 1
                if slash >= 0.35 * len(cont):  # check bad encoding docs
                    apd = True

        if apd:  # delete invalid docs
            os.remove(relf)
            print('{} is deleted!'.format(f))
        else:
            with open(relf, 'r') as fr:
                linels = []
                for line in fr:
                    sig = re.search(r'(/.){2,}/', line)
                    if sig:
                        line = re.sub('[^{}]/'.format(self._cmchinese), '', line)
                        line = re.sub(r'(/.){3,}/', '/', line)
                    linels.append(line + '\n')
            with open(relf, 'w+') as fwt:
                fwt.writelines(linels)

    @staticmethod
    def _get_char_list(cmchinese):

        fonts_range = []
        with open(cmchinese, 'r') as fr:
            for line in fr:
                fonts_range.extend(map(lambda x: re.sub(r'^0x', r'\u', x),
                                       re.split(',', line.strip().strip(','))))

        letter_list = ''.join(yf.encode('utf-8').decode('unicode_escape') for yf in fonts_range)
        return letter_list


def run(path):
    for file in os.listdir(path):
        Partition(doc=path + file)


if __name__ == '__main__':
    run(testpath)