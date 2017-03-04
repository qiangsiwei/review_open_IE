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

def select_sample(comment_file):
	# positive = ur'(?<![无不没])(顺|滑|柔|爽|润|舒服)'
	# negative = ur'(?<![无不没])(油|痒|干燥|毛躁|屑)'
	prevtense = ur'((?<!#P\s)(?<!#P\s#PN\s)(?<!#CC\s)(?<!#CC\s#PN\s)(以前|之前|先前|原先|以往|上次|平时|最近))' # 原来|一直
	count, duplicate = 0, {}
	with open('../data/trainset.txt','w') as f:
		for line in fileinput.input(comment_file):
			line = line.strip().decode('utf-8')
			txt = u''.join([re.sub(ur'#[^#]*$','',e) for e in line.split(u' ')])
			ext = re.sub(ur'[^以之先前原以往上次平时最近\s]+(#[^\s]+)',ur'\1',line)
			subsens = [subsen.strip() for subsen in re.split(ur'\s[^\s]*#PU', line) if u'#' in subsen]
			if len(txt)>=10 and len(txt)<=100 and len(subsens)>=2 and not txt in duplicate and re.findall(prevtense,ext):
				# print fileinput.lineno(), txt
				for subsen in subsens:
					subext = re.sub(ur'[^以之先前原以往上次平时最近\s]+(#[^\s]+)',ur'\1',subsen)
					label = 1 if len(re.findall(prevtense,subext))!=0 else 0
					f.write(u"{0}\t{1}\t{2}\n".format(str(count).zfill(5),label,subsen).encode('utf-8'))
				f.write('\n')
				count += 1
				duplicate[txt] = True
		fileinput.close()
	print count

def tagging_tense(comment_file):
	prevtense = ur'((?<!#P\s)(?<!#P\s[^\s]#PN\s)(?<!#CC\s)(?<!#CC\s[^\s]#PN\s))(以前|之前|先前|原先|以往|上次|平时|最近)'
	posttense = ur'(这个|这款|这次|昨天|今天|现在|下次)'
	retense = ur'|(?<=[。？！]#PU)\s'
	for line in fileinput.input(comment_file):
		line = line.strip().decode('utf-8')
		prevstart = list((m.start(),1) for m in re.finditer(prevtense, line))
		poststart = list((m.start(),0) for m in re.finditer(posttense, line))
		if poststart:
			poststart = list((m.start(),0) for m in re.finditer(posttense+retense, line))
		else:
			poststart = list((m.start(),0) for m in re.finditer(ur'(?<=#PU)\s', line))
		if prevstart:
			last, slices = 0, [0]
			for position,tense in sorted(prevstart + poststart):
				if tense != last:
					slices.append(position)
					last = tense
			slices.append(len(line)-1)
			colorlist, color = [colors.red, colors.green], False
			for i in xrange(len(slices)-1):
				print colorlist[color], line[slices[i]:slices[i+1]],
				color = not color
			print colors.close
	fileinput.close()

if __name__ == '__main__':
	comment_file = '../data/tmall-xifashui-20160128.txt.valid.comment.tagged'
	# select_sample(comment_file)
	tagging_tense(comment_file)
