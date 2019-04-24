#!/usr/bin/env python
# -*- coding: utf8 -*-


"""
	This module contains the class Source.
	======================================
"""
from ObjToIndex import ObjToIndex
import os, sys
install_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../../../'
getConfPath = install_dir + 'services/modules/common'
sys.path.insert(0, getConfPath)
import getConf
from IndexSource import IndexSource
from time import strftime
import dateutil.parser
import logging
logger = logging.getLogger(__name__)

class Source(ObjToIndex):
	"""
		Source class represents a feed and its informations.

		It inherits from ObjToIndex class.
	"""

	def __init__(self, cfgPath):
		"""
			Source class' constructor.

			:param config: Config object that contains informations about the feed.
			:type config: Config object instance.
		"""
		self.cfgPath = cfgPath
		#conf from hippocampe/core/conf/feeds
		conf = getConf.getConf(cfgPath)

		#conf from hippocampe/core/conf/hippo
		cfg = getConf.getHippoConf()

		super(Source, self).__init__()
		self.source = conf.get('source', 'url')
		self.firstQuery =  str()
		self.lastQuery = str()
		self.description = conf.get('source', 'description')

		self.indexNameES = cfg.get('elasticsearch', 'indexNameES')
		self.typeNameES = cfg.get('elasticsearch', 'typeNameESSource')

		self.score = conf.getint('source', 'score')
		self.coreIntelligence = conf.get('source', 'coreIntelligence')
		self.typeNameESIntel = conf.get('elasticsearch', 'typeIntel')
		self.validityDate = conf.get('source', 'validityDate')
		self.useByDate = conf.get('source', 'useBydate')

	def forgeDocSearch(self):
		"""
			Forges the search query to search source in elasticsearch.
		"""
		self.docSearch = {
		    "query": {
		        "bool": {
		            "must": [
		                {
		                    "match": {
		                        "link": self.source
		                    }
		                }
		                #{
		                #    "match": {
		                #        "type": self.typeNameES
		                #    }
		                #}
		            ]
		        }
		    }
		}


	def forgeDocIndex(self):
		"""
			Forges the index query to index source in elasticsearch.
		"""
		self.docIndex = {
		    "link": self.source,
		    "type": self.typeNameESIntel,
		    "firstQuery": self.firstQuery,
		    "lastQuery": self.lastQuery,
		    "description": self.description,
		    "score": self.score,
		    "coreIntelligence": self.coreIntelligence
		}

	def forgeDocUpdateLastQuery(self):
		"""
			Forges the update query to update source in elasticsearch.
		"""
		self.docUpdate = {
		    "script": {
				"lang": "painless",
				"source": "ctx._source.lastQuery = params.lastQuery",
		    	"params": {
		        	"lastQuery": self.lastQuery
		    	}
			}
		}

	def forgeDocUpdateScore(self):
		self.docUpdate = {
			"script": {
				"lang": "painless",
				"source": "ctx._source.score = params.score",
				"params": {
					"score": self.score
				}
			}
		}

	def getScoreInES(self):
		"""
			Returns the source's score as it is indexed in ES and
			not as in the conf file
		"""
		return self.resSearch['hits']['hits'][0]['_source']['score']

	def indexSourceInES(self):
		indexSource = IndexSource(self.cfgPath)
		#creating the index only if does not already exist
		#the method will check by itself
		indexSource.createIndexSource()

		#first, searching if the source exists before indexing it
		self.forgeDocSearch()
		nbMatch = self.search()
		if nbMatch == 0:
			logger.info('%s querried for the first time', self.source)
			#no match, setting firstQuery and lastQuery to current time
			self.firstQuery = strftime("%Y%m%dT%H%M%S%z")
			self.lastQuery = strftime("%Y%m%dT%H%M%S%z")
			self.forgeDocIndex()
			self.indexInES()
		if nbMatch > 0:
			#match, updating lastQuery
			logger.info('Updating %s lastQuery', self.source)
			self.lastQuery = strftime('%Y%m%dT%H%M%S%z')
			self.forgeDocUpdateLastQuery()
			self.update()
	                #the source exists in ES
                        #checking if the source's score in ES and in conf file
                        #are the same, if not, updating in ES
			if self.score != self.getScoreInES():
                                self.forgeDocUpdateScore()
                                self.update()

	def isActive(self):
		logger.info('Source.isActive starts')
		#A
		if self.validityDate != '' and self.useByDate == '':
			logger.info('A scenario')
			return True
		#B
		elif self.validityDate == '' and self.useByDate != '':
			logger.info('B scenario')
			return False
		#E
		elif self.validityDate == '' and self.useByDate == '':
			logger.info('E scenario')
			return True

		#converting in datetime
		today = strftime('%Y%m%d')
		today = dateutil.parser.parse(today)
		useByDate = dateutil.parser.parse(self.useByDate)
		validityDate = dateutil.parser.parse(self.validityDate)
		#C
		if validityDate < useByDate:
			if today < validityDate and today < useByDate:
				logger.info('C scenario (C1), source is inactive')
				return False
			elif validityDate < today and today < useByDate:
				logger.info('C scenario (C2), source is active')
				return True
			elif today > validityDate and today > useByDate:
				logger.info('C scenario (C3), source is inactive')
				return False
		#D
		elif useByDate < validityDate:
			if today < useByDate and today < validityDate:
				logger.info('D scenario (D1), source is active')
				return True
			elif useByDate < today and today < validityDate:
				logger.info('D scenario (D2), source is inactive')
				return False
			elif today > useByDate and today > validityDate:
				logger.info('D scenario (D3), source is active')
				return True
