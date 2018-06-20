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

pathfrom = '/home/yy/usstock/usstockresearch/'
pathto = '/home/yy/usstock/usstockcut/'
stopws = '/home/yy/usstock/stop_words_v0520.txt'
mydic = r'/home/yy/usstock/abcChinesegamma.txt'
cmchinese = '/home/yy/usstock/commonchinese.txt'

mode1 = '本报告由中国国际金融股份有限公司.+\n'
mode2 = '在此申明，本报告所表述的所有观点.+?研究行业及评级：分析师给出.+\n'
mode3 = '分析师声明.+?评级说明.+\n'
mode4 = '免责声明及披露.+?分析员声明.+\n'
mode5 = '本报告署名分析师在此声明.+\n'
mode6 = '披露声明.+?评级体系说明.+\n'
mode7 = '投资评级定义.+?监管披露.+?免责条款.+\n'
mode8 = '作者具有中国证券业协会授予的证券投资咨询执业资格，保证报告.+\n'
mode9 = '新三板团队介绍.+?公司业绩点评报告.+\n'
mode10 = '披露声明.+?本报告准确表述了分析员的个人观点.+\n'
mode11  = '本报告中的信息均来源于已公开的资料.+?或引用。'
mode12 = '西藏东方财富证券股份有限公司.+?分析师申明.+\n'
mode13 = '广发海外消费研究小组.+?行业投资评级说明.+\n'
mode14 = '分析师承诺.+?国海证券投资评级标准.+\n'



class PartofSpeech:
    initial = 0

    def __init__(self, pathfrom, pathto, doc=None, stopws=stopws, mydic=mydic, cmchinese=cmchinese):
        """pathfrom is the path where docs restore, and pathto the path docs write into. If doc is supplied, doc must be a
        txt file with abslute directory."""
        self.doc = doc
        self.pathfrom = pathfrom
        self.pathto = pathto
        if PartofSpeech.initial == 0:
            jieba.load_userdict(mydic)
        PartofSpeech.initial += 1
        self._stopws = PartofSpeech._getstp(stopws)
        self._cmchinese = PartofSpeech._get_char_list(cmchinese)
        if not doc:
            for file in os.listdir(self.pathfrom):
                if file.endswith('.txt') and os.path.getsize(self.pathfrom + file):
                    self._parttofile(file)
        else:
            self.pathfrom = os.path.split(doc)[0]
            self._parttofile(os.path.split(doc)[1])

    @staticmethod
    def _getstp(stopws):
        """obtain stop words from file"""
        with open(stopws, 'r', encoding='utf-8') as rs:
            stpws = rs.read()
        return stpws

    @staticmethod
    def _is_chinese(uchar):
        """check if uchar is a chinese character"""
        return all([True if ele >= u'\u4e00' and ele <= u'\u9fa5' else False for ele in uchar])

    def _preprocess(self, f):
        tot = ''
        fils = []
        nul = re.compile(r'\s{5,}')
        rule = re.compile(r'(\d+?.?\d*%?\s+)+')
        mode = re.compile('{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(mode1, mode2, mode3, \
                                                                             mode4, mode5, mode6, mode7, mode8, \
                                                                             mode9, mode10, mode11, mode12, mode13,
                                                                             mode14), flags=re.S)
        with open(self.pathfrom + f, 'r') as frt:
            cont = frt.read()
            cl = mode.sub('', cont)
        with open(self.pathfrom + f, 'w') as fw:
            fw.write(cl)
        with open(self.pathfrom + f, 'r') as fr:
            fline = fr.readline()
            while fline:
                if not re.search(nul, fline) and not re.search(rule, fline):
                    if not re.search('，|。', fline):
                        fils.append(fline.strip())
                        fline = fr.readline()
                        continue
                    incmp = fline
                    while fline and not fline.rstrip().endswith('。'):
                        fline = fr.readline()
                        incmp += fline.rstrip()
                    fils.append(incmp.strip())
                fline = fr.readline()
        return fils

    def _partition(self, corpsch):
        cuted = []
        for sent in corpsch:
            sent = re.sub(r'\s|\W|[a-z]|[A-Z]', '', sent)
            if sent:
                sent = Converter('zh-hans').convert(sent)  # # traditinal chinese transfromation
                segs = jieba.cut(sent)
                cutsent = '/'.join(ele for ele in segs if self._is_chinese(ele) and ele not in self._stopws)
                cuted.append(cutsent)
        return cuted

    def _parttofile(self, f):
        relf = self.pathto + 'part' + f
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

if __name__ == '__main__':
    PartofSpeech(pathfrom, pathto)
