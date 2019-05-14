#!/usr/bin/env python
# -*- coding: utf8 -*-


"""
	This module contains the class IndexSource.
	===========================================
"""
from Index import Index
import os, sys
install_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../../../'
getConfPath = install_dir + 'services/modules/common'
sys.path.insert(0, getConfPath)
from getConf import getHippoConf

class IndexSource(Index):
	"""
		IndexIOC class represents an elasticsearch's index. And more precisely
		an index storing source.

		The class inherits from Index class.
	"""

	def __init__(self, cfgPath):
		"""
			IndexSource class' constructor.

			:param source: shadowBook process's configuration
			:type config: Config object instance
		"""
		conf = getHippoConf()

		super(IndexSource, self).__init__()
		self.indexNameES = conf.get('elasticsearch', 'indexNameES')
		self.typeNameES = conf.get('elasticsearch', 'typeNameESSource')


	def forgeDocMapping(self):
		"""
			Forges the elasticsearch's mappings for IndexSource.
		"""
		self.docMapping = {
		        self.typeNameES: {
		            "properties": {
						"lastStatus": {
							"type": "keyword"
						},
		                "link": {
		                    "type": "keyword"
		                },
		                "type": {
		                    "type": "keyword"
		                },
		                "firstQuery": {
		                    "type": "date",
		                    "format": "basic_date_time_no_millis"
		                },
		                "lastQuery": {
		                    "type": "date",
		                    "format": "basic_date_time_no_millis"
		                },
		                "description": {
                                    "fielddata": True,
		                    "type": "text"
		                },
		                "score": {
		                    "type": "integer"
		                },
		                "coreIntelligence": {
		                    "type": "keyword"
		                }
		            }
		        }
		    }

	def createIndexSource(self):
		self.forgeDocMapping()
		self.create()
