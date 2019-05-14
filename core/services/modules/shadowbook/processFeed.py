#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
from objects.Source import Source
from downloader import simpleDownload, EmptyFeedException
import searchIntel
import processMsearch
import bulkOp
import enricher
import extendTools

import operator
import requests
from parser import csvParser
from configparser import NoOptionError, NoSectionError
from objects.Intel import Intel
import logging
logger = logging.getLogger(__name__)

from pprint import pprint
def main(listSessions, cfgPath):
	confName = os.path.basename(os.path.normpath(cfgPath))

	logger.info('processFeed.main launched for %s', confName)
	#the function returns a report concerning the feed process
	#the instructions below are used to build the report
	report = dict()
	report[confName] = dict()
	report[confName]['error'] = list()
	nbUpdate = 0
	nbIndex = 0
	nbNew = 0
	nbFailed = 0
	sourceActivated = bool()
	
	try:
		source = Source(cfgPath)
		#adding the source's url to the report
		report[confName]['link'] = source.source

		#either True or False
		sourceActivated = source.isActive()

		if sourceActivated:
			#index the source's data into ES if it does not already exist
			#if it does, update the lastQuery date and make sure that the source's score in ES
			#equals the source's score in conf file
			#conf file's score is the reference and will always be pushed to ES
			source.indexSourceInES()
			
			try:
				#downloading feed with authenticated sessions
				#streaming mode
				feedPage = simpleDownload(source.source, listSessions)
				if len(feedPage) == 0:
					raise EmptyFeedException(source.source)
				try:
					#the cfgPath is given in parameters because it contains the delimiter
					#the function will return a csvDictReader which we convert to dict afterward
					parsedPage = csvParser(feedPage, cfgPath)
					parsedPage = list(extendTools.unique_justseen(list(parsedPage), key = operator.itemgetter(source.coreIntelligence)))
					#parsedPage will look like:
					#[{'domain': 'stie.pbsoedirman.com', 'original_reference-why_it_was_listed': 'spamhaus.org', u'extra': ['20160324'], 'nextvalidation': '', 'blank': '', 'type': 'malware'}, {'domain': 'thecommercialalliance.com', 'original_reference-why_it_was_listed': 'spamhaus.org', u'extra': ['20160324'], 'nextvalidation': '', 'blank': '', 'type': 'botnet'}]
					
					#searching all intels at once with msearch
					resMsearch = searchIntel.littleMsearch(source.coreIntelligence, source.typeNameESIntel, parsedPage)
					#logger.debug('resMsearch = %s', resMsearch)
					#sorting intels which will be updated and indexed
					sortedDict = processMsearch.littleSort(resMsearch, parsedPage)
					
					if len(sortedDict['toUpdate']) > 0:
						#updating
						#sortedDict['toUpdate'] is a list, each element is a doc's id
						nbUpdate = bulkOp.update(source.typeNameESIntel, sortedDict['toUpdate'])

					if len(sortedDict['toIndex']) > 0:
						#indexing
						#intels which have never been seen before are indexed under type new
						#in addition to the type <source.typeNameESIntel> 
						#sortedDict['toIndex'] is a list, each element is a dict representing a feed's parsed line
						resMsearch = searchIntel.bigMsearch(source.coreIntelligence, sortedDict['toIndex'])
						toIndexInNew = processMsearch.bigSort(resMsearch, sortedDict['toIndex'])
						#toIndexInNew is a list, each element is a dict representing a feed's parsed line which intel has never been seen before
						#indexing only the coreIntelligence
						nbNew = bulkOp.indexNew(source.coreIntelligence, toIndexInNew)
						toIndex = enricher.metadata(source.idInES, source.source, sortedDict['toIndex'])
						res = bulkOp.index(cfgPath, toIndex)
						#res looks like
						#(1337, [{u'create': {u'status': 400, u'_type': u'type', u'_id': u'AVSFZmDLGOrJYzzqtBgw', u'error': u'MapperParsingException[failed to parse [ip]]; nested: ElasticsearchIllegalArgumentException[failed to parse ip [nxdomain], not a valid ip address]; ', u'_index': u'hippocampe'}}, {u'create': {u'status': 400, u'_type': u'type', u'_id': u'AVSFZmDLGOrJYzzqtBg0', u'error': u'MapperParsingException[failed to parse [ip]]; nested: ElasticsearchIllegalArgumentException[failed to parse ip [nxdomain], not a valid ip address]; ', u'_index': u'hippocampeinte'}}])
						logger.info(type(res))
						nbIndex = res[0]
						if len(res) > 1:
							nbFailed = len(res[1])
							for bulkReport in res[1]:
								report[confName]['error'].append(bulkReport['create']['error'])
						
						
					
				except NoSectionError as e:
					logger.error('fail in parsing %s for the parser', confName, exc_info = True)
					report[confName]['error'].append(str(e))
				except NoOptionError as e:
					logger.error('fail in parsing %s file for the parser', confName, exc_info = True)
					report[confName]['error'].append(str(e))
				except EmptyFeedException as e:
					logger.error(e, exc_info = True)
					report[confName]['error'].append(str(e))
			except requests.exceptions.RequestException as e:
				logger.error('downloading %s failed', source.source, exc_info = True)
				#filling in the report
				report[confName]['error'].append(str(e))
	except NoSectionError as e:
		logger.error('fail in parsing %s for the source', confName, exc_info = True)
		report[confName]['error'].append(str(e))
	except NoOptionError as e:
		logger.error('fail in parsing %s for the source', confName, exc_info = True)
		report[confName]['error'].append(str(e))
	except Exception as e:
		logger.error('processFeed.main failed for %s, no idea where it came from', confName, exc_info = True)
		report[confName]['error'].append(str(e))

	report[confName]['nbIndex'] = nbIndex
	report[confName]['nbUpdate'] = nbUpdate
	report[confName]['activated'] = sourceActivated
	report[confName]['nbNew'] = nbNew
	report[confName]['nbFailed'] = nbFailed

	#the report looks like
	#{'dnsbh_DOMAIN.conf': {'error': [], 'nbFail': 0, 'nbSucess': 13921}}
	logger.info('processFeed.main for %s end', confName)
	return report
			
if __name__ == '__main__':
	main()
