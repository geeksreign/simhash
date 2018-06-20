# simhash
delete duplicates of US stock corporation research documents with simhash algorithm

数据集为美股公司研究报告文档，共约1000个；
这个文本去重任务大致分为两个步骤，分词和去重，分别于partofspeech.py和findsimilar.py中实现；
这里的实现考虑去重对象主要为文本内容以中文（简繁）以及中文为主的文本，过滤了纯英文和编码错误的文本；

用到的外部package包括jieba，simhash（可用pip直接安装）和langconv，后者用于中文简繁转换；
此外，额外准备了分词会用到的停止词，个人词典，常用汉字（约3500个，用于去除局部中文乱码）和简繁对照文件。

