#!/usr/bin/env python
# -*- coding: utf8 -*-


from Index import Index
import os, sys
app_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../../../'
getConfPath = app_dir + 'services/modules/common'
sys.path.insert(0, getConfPath)
from getConf import getHippoConf
from itertools import izip_longest
import ast
import logging

logger = logging.getLogger(__name__)
class IndexJob(Index):
	"""
		IndexIOC class represents an elasticsearch's index. And more precisely
		an index storing IOC.

		The class inherits from Index class.
	"""

#	def __init__(self, cfgPath):
	def __init__(self):

		super(IndexJob, self).__init__()
		cfg = getHippoConf()
		self.indexNameES =  cfg.get('elasticsearch', 'indexNameES')
		self.typeNameES = cfg.get('elasticsearch', 'typeNameESJobs')

		#the mapping has to be indicated at the creation of the index
		#the confMapping, is the mapping indicated in conf file for each field
		#it has to be parsed bellow
		self.confMapping = dict()

	def forgeDocMapping(self):
		"""
			Forges the elasticsearch's mappings for IndexIOC.
		"""
		#mapping for the meta-data
		self.docMapping = {
			self.typeNameES : {
#				"dynamic": "strict",
				"properties" : {
#					"report": {
#						"type": "date"
#					},
					"status": {
						"type": "keyword"
					},
					"startTime": {
						"type": "date",
						"format": "basic_date_time_no_millis"
					},
					"endTime": {
						"type": "date",
						"format": "basic_date_time_no_millis"
					},
					"duration": {
						"type": "float"
					}
				}
			}
		}

	def createIndexJob(self):
		self.forgeDocMapping()
		self.create()
