#!/usr/bin/env python
# -*- coding: utf8 -*-


"""
	This module contains the class Index
	====================================
"""
from elasticsearch import client
import os, sys
install_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../../../'
pathModule = install_dir + 'services/modules/common'
sys.path.insert(0, pathModule)
from ES import getES
import logging
logger = logging.getLogger(__name__)
class Index(object):
	"""
		Index class represents an elasticsearch's index.

		This class is kind of an abstract class, because it is the common base
		of IndexSource and IndexIOC classes.
	"""

	def __init__(self):
		"""
			Index class' constructor.
		"""

		self.indexNameES = str()
		self.typeNameES = str()
		self.docMapping = dict()
		self.es = getES()
		#self.logger = logging.getLogger('app.shadowbook')		
		
	def create(self):
		#create indexES instance
		indexES = client.IndicesClient(self.es)
		if(self.es.indices.exists(index = self.indexNameES)):
			logger.info('index %s already exists', self.indexNameES)
			#index already exists but it does not mean that the type exists
			if(self.es.indices.exists_type(index = self.indexNameES, doc_type = [self.typeNameES])):
				logger.info('type %s already exists', self.typeNameES)
				#type already exists nothing to do
				pass
			else:
				#type does not exists, creating it with the mapping to apply
				logger.info('type %s does not exist, creating it', self.typeNameES)
				indexES.put_mapping(doc_type = self.typeNameES, body = self.docMapping, index = self.indexNameES)
		else:
			#index does not exists, neither type (type can't exist without index)
			#creating both
			logger.info('index %s and type %s do not exist, creating them', self.indexNameES, self.typeNameES)
			indexES.create(index = self.indexNameES)
			#indicate mapping which applies only on index/type
			indexES.put_mapping(doc_type = self.typeNameES, body = self.docMapping, index = self.indexNameES)
