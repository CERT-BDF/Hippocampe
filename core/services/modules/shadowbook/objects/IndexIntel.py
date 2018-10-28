#!/usr/bin/env python
# -*- coding: utf8 -*-


"""
	This module contains the class IndexIOC.
	========================================
"""
from Index import Index
import os, sys
install_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../../../'
getConfPath = install_dir + 'services/modules/common'
sys.path.insert(0, getConfPath)
import getConf
from itertools import izip_longest
import ast
class IndexIntel(Index):
	"""
		IndexIOC class represents an elasticsearch's index. And more precisely
		an index storing IOC.

		The class inherits from Index class.
	"""

	def __init__(self, cfgPath):
		"""
			IndexIOC class' constructor.

			:param config: shadowBook process's configuration
			:type config: Config object instance
		"""

		super(IndexIntel, self).__init__()
		self.conf = getConf.getConf(cfgPath)
		hippoConf = getConf.getHippoConf()
		self.indexNameES = hippoConf.get('elasticsearch', 'indexNameES')
		self.typeNameES = self.conf.get('elasticsearch', 'typeIntel')

		#the mapping has to be indicated at the creation of the index
		#the confMapping, is the mapping indicated in conf file for each field
		#it has to be parsed bellow
		self.confMapping = dict()

	def buildConfMapping(self):
		def listToDict(inputList):
			"""
			Little function that converts a list into a dict.

			This function is needed because ConfigParser.items() returns all options
			from a given section as a list. A dict is more user-freindly to use.

			:param inputList: list to be converted into dict
			:type inputList: list
			:return: the list converted as a dict
			:rtype: dict
			"""
			dictOutput = dict()
			for couple in inputList:
				tmpDict = dict(izip_longest(*[iter(couple)] * 2, fillvalue=''))
				for nameIoc, value in tmpDict.items():
					dictOutput[nameIoc] = value
			return dictOutput

		#items retrieve all options from 'intel' section, but as a list.
		#the list is converted to a dict
		listMapping = self.conf.items('intel')
		self.confMapping = listToDict(listMapping)
		#at the end, self.confMapping looks like this:
		#{u'domain': u'{\n"mapping" : {\n"type": "string",\n"index": "not_analyzed"\n}\n}',
		# u'extra': u'{\n"mapping" : {\n"type": "string",\n"index": "not_analyzed"\n}\n}',
		# u'nextvalidation': u'{\n"mapping" : {\n"type": "string",\n"index": "not_analyzed"\n}\n}',
		# u'original_reference-why_it_was_listed': u'{\n"mapping" : {\n"type": "string",\n"index": "not_analyzed"\n}\n}',
		# u'type': u'{\n"mapping" : {\n"type": "string",\n"index": "not_analyzed"\n}\n}'}
		#However, please note that the key AND the value is unicode
		#so u'{\n"mapping" : {\n"type": "string",\n"index": "not_analyzed"\n}\n}'} is a unicode
		#formated as a string

	def forgeDocMapping(self):
		"""
			Forges the elasticsearch's mappings for IndexIOC.
		"""
		#mapping for the meta-data
		self.docMapping = {
			self.typeNameES : {
				"properties" : {
					"firstAppearance": {
						"type": "date",
						"format": "basic_date_time_no_millis"
					},
					"idSource": {
						"type": "keyword"
					},
					"lastAppearance": {
						"type": "date",
						"format": "basic_date_time_no_millis"
					},
					"source": {
						"type": "keyword"
					}
				}
			}
		}
		for intel, conf in self.confMapping.items():
			#adding ioc's mapping
			#conf here is a unicode formated as a dict, has to actually "convert" it to dict
			dicoTmp = ast.literal_eval(conf)
			self.docMapping[self.typeNameES]['properties'][intel] = dicoTmp['mapping']
		#at the end, the docMapping looks like this:
		#{u'malwaredomainsFree_dnsbhDOMAIN': {'properties': {u'domain': {'index': 'not_analyzed',
		#                                                                'type': 'string'},
		#                                                    u'extra': {'index': 'not_analyzed',
		#                                                               'type': 'string'},
		#                                                    'firstAppearance': {'format': 'basic_date_time_no_millis',
		#                                                                        'type': 'date'},
		#                                                    'idSource': {'type': 'string'},
		#                                                    'lastAppearance': {'format': 'basic_date_time_no_millis',
		#                                                                       'type': 'date'},
		#                                                    u'nextvalidation': {'index': 'not_analyzed',
		#                                                                        'type': 'string'},
		#                                                    u'original_reference-why_it_was_listed': {'index': 'not_analyzed',
		#                                                                                              'type': 'string'},
		#                                                    'source': {'type': 'string'},
		#                                                    u'type': {'index': 'not_analyzed',
		#                                                              'type': 'string'}}}}
		#

	def createIndexIntel(self):
		self.buildConfMapping()
		self.forgeDocMapping()
		self.create()
