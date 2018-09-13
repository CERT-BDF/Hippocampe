#!/usr/bin/env python
# -*- coding: utf8 -*-


from time import strftime
from modules.hipposcore.ExistingSource import ExistingSource
import dateutil.parser
from math import exp
from werkzeug.contrib.cache import SimpleCache
import logging
logger = logging.getLogger(__name__)
def calcHipposcore(dictResult):
	logger.info('hipposcore.calcHipposcore launched')
	try:
		T = 182.625
		n1 = float()
		n2 = float()
		n3 = float()
		#the final result
		hippodict = dict()
		#json object for hipposcore
		#{
		#	'ioc': {
		#		'hipposcore': -89
		#	}
		#}
		scoredict = dict()
		now = strftime("%Y%m%dT%H%M%S%z")
		P = float()
		#a cache is used to speed up the source's score retrieve
		cache = SimpleCache()
		
		for ioc, listMatches in dictResult.items():
			#if there is no match for the ioc
			#listmaches will be empt, then hipposcore will be 0
			if not listMatches :
				hippodict[ioc] = dict()
				hippodict[ioc]['hipposcore'] = 0
			#match case
			else:
				P = 0.0
				for match in listMatches:
					try:
						#n1 retrieving the source according to its id
						idSource = match['idSource']
						n1 = cache.get(idSource)
						if n1 is None:
							source = ExistingSource(idSource)
							source.forgeDocMatch()
							if source.search():
								source.processMatchResponse()
								n1 = source.getScore()
								#the source's scor is between -100 and +100
								#for convenience,
								#in the formula it is required to be within -1 and +1
								n1 = n1 / 100.0
								cache.set(idSource, n1, timeout=3 * 60)
						#n2
						#rank is specific to alexa feed
						if 'rank' in match:
							n2 = match['rank']
						else:
							n2 = 1.0
						#n3
						#last time hippocampe saw the ioc
						lastAppearance = match['lastAppearance']
						#lastAppearance is a string, to calculate the time 
						#difference, in other word the age of the ioc,
						#between lastAppearance and now, it is
						#needed to convert those strings to date
						lastAppearanceDate = dateutil.parser.parse(lastAppearance)
						nowDate = dateutil.parser.parse(now)
						#ioc's age in days
						age = (nowDate - lastAppearanceDate).days
						n3 = exp(-age / T)
						P = P + (n3 * n2 * n1)
					except Exception as e:
						logger.error('hipposcore.calcHipposcore.match failed to process', exc_info = True)
						logger.error(match)
						report = dict()
						report['error'] = str(e)

				score = (1 - exp(-2 * abs(P))) * (abs(P) / P) * 100
				score = "%.2f" % score
				scoredict['hipposcore'] = score
				#scoredict['hipposcore'] = (1 - exp(-2 * abs(P))) * (abs(P) / P) * 100
				hippodict[ioc] = scoredict
		logger.info('hipposcore.main end')
		return hippodict
	except Exception as e:
		logger.error('hipposcore.calcHipposcore failed, no idea where it came from...', exc_info = True)
		report = dict()
		report['error'] = str(e)	
if __name__ == '__main__':
	calcHipposcore()
