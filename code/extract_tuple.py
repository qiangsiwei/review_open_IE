# -*- encoding:utf-8 -*-

import os
import re
import math
import time
import fileinput
import numpy as np
from bbl.lib.nlp.voice_extract.top_com import extract_nv_pairs
from bbl.lib.misc.lin_tools import str2unicode
from datetime import datetime

class colors:
	red = '\033[91m'
	green = '\033[92m'
	close = '\033[0m'

def extract_rulebased(comment_file):
	with open(comment_file, 'r') as f:
		reviews = [str2unicode(line.strip('\n')) for line in f][:100]
	print "reviews", len(reviews), datetime.now()
	nvls = extract_nv_pairs(reviews, need_fill=True)
	for review, nvl in zip(reviews,nvls):
		for nv in nvl:
			if nv[0] != u'empN' and nv[1] != u'empV':
				print '|'.join([nv[0], nv[1]]), review

def statistic_pos(comment_file, target):
	pos_statisticistic = {}
	for line in fileinput.input(comment_file):
		for word, pos in [(u'#'.join(entry.split(u'#')[:-1]),entry.split(u'#')[-1]) for entry in line.strip('\n').decode('utf-8').split(' ')]:
			pos_statisticistic[pos] = pos_statisticistic.get(pos,{})
			pos_statisticistic[pos][word] = pos_statisticistic[pos].get(word,0)+1
		if fileinput.lineno() == 10**4:
			break
	fileinput.close()
	print ','.join([entry['word'] for entry in sorted([{'word':word,'count':count} for word, count in \
				pos_statisticistic.get(target,{}).iteritems()],key=lambda x:x['count'],reverse=True)[:20]])

def preprocess_word2vec(comment_file):
	with open('../data/segmented.txt','w') as f:
		for line in fileinput.input(comment_file):
			line = u' '.join([u'#'.join(entry.split(u'#')[:-1]) for entry in line.strip('\n').decode('utf-8').split(' ')]).encode('utf-8')
			f.write('{0}\n'.format(line))
		fileinput.close()

def extract_simple(comment_file):
	pn, pv = ur'(N[NR])|(PN)', ur'(V[AVEC])|(JJ)'
	statistic = {}
	for line in fileinput.input(comment_file):
		subsens = [subsen.strip() for subsen in re.split(ur' .#PU', line.strip().decode('utf-8')) if u'#' in subsen]
		txt = [[p.split(r'#')[0] for p in subsen.split(' ')] for subsen in subsens]
		pos = [[p.split(r'#')[1] for p in subsen.split(' ')] for subsen in subsens]
		cls = [re.sub('2(?=2)','0',''.join(['1' if re.match(pn,p) else '2' if re.match(pv,p) else '0' for p in subpos])) for subpos in pos]
		for index, (subtxt, subcls) in enumerate(zip(txt,cls)):
			# nouns = [subtxt[i] for i in range(len(subcls)) if subcls[i]=='1']
			# verbs = [subtxt[i] for i in range(len(subcls)) if subcls[i]=='2']
			if subcls.count('1')==1 and subcls.count('2')==1:
				# print fileinput.lineno(), subsens[index]
				# print "nouns:", '|'.join(nouns), "verbs:", '|'.join(verbs)
				start, end = min(subcls.index('1'),subcls.index('2')), max(subcls.index('1'),subcls.index('2'))
				sequence_txt = ' '.join(subtxt[start:end+1])
				sequence_pos = ' '.join(pos[index][start:end+1])
				# print sequence_pos, sequence_txt
				statistic[sequence_pos] = statistic.get(sequence_pos,{'cnt':0,'top':{}})
				statistic[sequence_pos]['cnt'] += 1
				statistic[sequence_pos]['top'][sequence_txt] = statistic[sequence_pos]['top'].get(sequence_txt,0)+1
	fileinput.close()
	statistic = sorted([{'pattern':k,'cnt':v['cnt'],'top':v['top']} for k,v in statistic.iteritems()],key=lambda x:x['cnt'],reverse=True)[:20]
	for pattern in statistic:
		print u'{0}:{1}\t'.format(pattern['pattern'], pattern['cnt']),
		for instance in sorted([{'instance':k,'cnt':v} for k,v in pattern['top'].iteritems()],key=lambda x:x['cnt'],reverse=True)[:3]:
			print u'|{0}:{1}'.format(instance['instance'], instance['cnt']),
		print

# 名、动词出现情况统计
# {0: 44330, 1: 513195, 2: 122487, 3: 133725, 4: 481308, 5: 172884, 6: 58568, 7: 160408, 8: 171725}
# 名相对于动词出现距离统计
# {-12: 1, -11: 4, -9: 8, -8: 22, -7: 82, -6: 306, -5: 1205, -4: 6642, -3: 37778, -2: 124358, -1: 133372, 1: 118493, 2: 44193, 3: 8399, 4: 5413, 5: 792, 6: 193, 7: 35, 8: 10, 10: 1, 11: 1}
# 名、动词Top(N)模式统计
# 273196(5)、354224(10)、388232(15)、405653(20)、417408(25)、424241(30)
# NN VA:62529		|东西 不错:3591 |发货 快:3432 |包装 不错:2450
# NN VV:62313		|包装 很好:5100 |宝贝 收到:4879 |东西 收到:2655
# NN AD VA:55102	|包装 很 严实:1916 |物流 也 快:1023 |包装 很 仔细:991
# VV NN:52862		|期待 效果:3656 |收到 货:3002 |值得 购买:1510
# NN AD VV:40390	|味道 很好 闻:3064 |东西 还 没用:1674 |包装 也 很好:1315
# VC NN:32146		|是 正品:28183 |是 真品:614 |是 假货:281
# JJ NN:17864		|大 瓶:1039 |很大 一瓶:588 |很大 瓶:465
# VV AS NN:11068	|送 了 吹风机:746 |送 了 赠品:606 |送 了 礼物:350
# VV DEC NN:9987	|送 的 礼物:210 |喜欢 的 味道:192 |用 的 洗发水:152
# VE NN:9963		|有 效果:1615 |没有 赠品:519 |无 硅油:458
# NN AD AD VA:9906	|包装 也 很 严实:207 |价格 也 很 实惠:162 |包装 也 很 仔细:134
# NN AD AD VV:8644	|味道 也 很好 闻:681 |东西 还 没有 用:339 |效果 还 不 知道:190
# VA DEC NN:6333	|满意 的 购物:254 |愉快 的 购物:218 |不错 的 宝贝:205
# NN VV VV:4679		|味道 挺好 闻:383 |店家 服务态度 很好:96 |朋友 介绍 买:41
# JJ DEG NN:4446	|很好 的 卖家:286 |好 的 效果:261 |很好 的 宝贝:204
# NN VV VA:4375		|物流 超 快:794 |发货 超 快:253 |卖家 服务态度 好:205
# VV DT NN:3624		|喜欢 这个 味道:441 |在用 这个 牌子:249 |喜欢 这个 牌子:226
# PN AD VV:3519		|我 很 喜欢:360 |这个 还 没用:149 |我 还 没用:94
# PN VV:3307		|我 喜欢:274 |这里 买:168 |我 用:135
# NR VV:2596		|聚划算 买:453 |祝生意 兴隆:77 |中 评:75

def compute_svd(comment_file, algorithm='nmf'):
	from sklearn.decomposition import NMF
	from sklearn.cluster.bicluster import SpectralBiclustering, SpectralCoclustering

	pn, pv = ur'(N[NR])|(PN)', ur'(V[AVEC])|(JJ)'
	nouns, verbs, tuples = {}, {}, {}
	for line in fileinput.input(comment_file):
		subsens = [subsen.strip() for subsen in re.split(ur' .#PU', line.strip().decode('utf-8')) if u'#' in subsen]
		txt = [[p.split(r'#')[0] for p in subsen.split(' ')] for subsen in subsens]
		pos = [[p.split(r'#')[1] for p in subsen.split(' ')] for subsen in subsens]
		cls = [re.sub('2(?=2)','0',''.join(['1' if re.match(pn,p) else '2' if re.match(pv,p) else '0' for p in subpos])) for subpos in pos]
		for index, (subtxt, subcls) in enumerate(zip(txt,cls)):
			if subcls.count('1')==1 and subcls.count('2')==1:
				noun = [subtxt[i] for i in range(len(subcls)) if subcls[i]=='1'][0]
				verb = [subtxt[i] for i in range(len(subcls)) if subcls[i]=='2'][0]
				nouns[noun] = nouns.get(noun,0)+1
				verbs[verb] = verbs.get(verb,0)+1
				tuples[(noun,verb)] = tuples.get((noun,verb),0)+1
	fileinput.close()
	noun_names = {entry['name']:index for index,entry in enumerate(sorted([{'name':name,'count':count} for name,count \
												in nouns.iteritems() if count >=10],key=lambda x:x['count'],reverse=True))}
	verb_names = {entry['name']:index for index,entry in enumerate(sorted([{'name':name,'count':count} for name,count \
												in verbs.iteritems() if count >=10],key=lambda x:x['count'],reverse=True))}
	noun_index = {v:k for k,v in noun_names.iteritems()}
	verb_index = {v:k for k,v in verb_names.iteritems()}
	
	n_clusters = 20
	matrix = np.zeros((len(noun_names),len(verb_names)))
	for (noun,verb), count in tuples.iteritems():
		if noun in noun_names and verb in verb_names:
			matrix[noun_names.get(noun)][verb_names.get(verb)] = math.log(count+1)
	print 'matrix shape:', matrix.shape
	
	# Non-Negative Matrix Factorization
	if algorithm == 'nmf':
		nmf = NMF(n_components=n_clusters, random_state=1, alpha=.1, l1_ratio=.5).fit(matrix)
		print 'reconstruction error:', nmf.reconstruction_err_
		for cluster in xrange(n_clusters):
			print '\ncluster: ', cluster
			for component, indexing in [(nmf.components_[cluster],verb_index),(np.transpose(nmf.transform(matrix))[cluster],noun_index)]:
				for entry in sorted([{'index':index,'value':value} for index,value in enumerate(component)],key=lambda x:x['value'],reverse=True)[:20]:
					print u'|{0}:{1}'.format(indexing.get(entry['index']),entry['value']),
				print

	# Spectral Co-Clustering
	if algorithm == 'biclustering':
		# model = SpectralBiclustering(n_clusters=n_clusters, random_state=0)
		model = SpectralCoclustering(n_clusters=n_clusters, random_state=0)
		model.fit(matrix)
		clusters = [{'nouns':{},'verbs':{}} for _ in range(n_clusters)]
		print len(model.row_labels_), len(model.column_labels_)
		for _index, _cluser in enumerate(model.row_labels_):
			clusters[_cluser]['nouns'][noun_index.get(_index)] = nouns.get(noun_index.get(_index))
		for _index, _cluser in enumerate(model.column_labels_):
			clusters[_cluser]['verbs'][verb_index.get(_index)] = verbs.get(verb_index.get(_index))
		for cluster in xrange(n_clusters):
			print '\ncluster: ', cluster
			print '|'.join([u'{0}:{1}'.format(e['k'],e['v']) for e in sorted([{'k':k,'v':v} for k,v in clusters[cluster]['nouns'].iteritems()])])
			print '|'.join([u'{0}:{1}'.format(e['k'],e['v']) for e in sorted([{'k':k,'v':v} for k,v in clusters[cluster]['verbs'].iteritems()])])
		
		from matplotlib import pyplot as plt
		fit_data = matrix[np.argsort(model.row_labels_)]
		fit_data = fit_data[:, np.argsort(model.column_labels_)]
		plt.matshow(fit_data, cmap=plt.cm.Blues)
		plt.title("Spectral Co-Clustering")
		plt.show()

if __name__ == '__main__':
	start = time.clock()
	comment_file = '../data/tmall-xifashui-20160128.txt.valid.comment.tagged'
	# statistic_pos(comment_file,'NN')
	# preprocess_word2vec(comment_file)
	# pattern_mining(comment_file)
	compute_svd(comment_file)
	elapsed = time.clock()-start
	print "\nTime used:", elapsed
