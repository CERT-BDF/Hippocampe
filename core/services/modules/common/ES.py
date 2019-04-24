#/usr/bin/env python
# -*- coding: utf8 -*-



from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from configparser import ConfigParser
import os
app_dir = os.path.dirname(os.path.abspath(__file__)) + '/../../../'
from getConf import getHippoConf
import logging
logger = logging.getLogger(__name__)

def getES():
	confPath = app_dir + '/conf/hippo/hippo.conf'
        cfg = ConfigParser()
        cfg.read(confPath)
        host = cfg.get('elasticsearch', 'ip')
        port = cfg.getint('elasticsearch', 'port')
		#estimeout = cfg.getint('elasticsearch', 'timeout')
        ES = Elasticsearch([{'host': host, 'port' : port}], timeout = 60)
	return ES

def checkES():
	logger.info('ES.checkES launched')
	try:
		ES = getES()
		return ES.ping()
	except Exception as e:
		logger.error('ES.checkES failed: %s', e, exc_info=True)

def checkData(checkList):
	#checkList is the list of types to check

	#check if the hippocampe's index exists in ES
	#and check if ES type exists according to checkList
	logger.info('ES.checkData launched')
	logger.info(checkList)
	ES = getES()
	index = IndicesClient(ES)

	cfg = getHippoConf()
	
	indexName = cfg.get('elasticsearch', 'indexNameES')
	#references contains the name of types used in Hippocampe
	references = dict()
	references['sourceType'] = cfg.get('elasticsearch', 'typeNameESSource')
	references['newType'] = cfg.get('elasticsearch', 'typeNameESNew')
	references['jobsType'] = cfg.get('elasticsearch', 'typeNameESJobs')

	#listType = list()
	#listType.append(sourceType)
	#listType.append(newType)
	#listType.append(jobsType) 	

	#check index
	if index.exists(index = indexName):
		#check types
		for check in checkList:
			if index.exists_type(index = indexName, doc_type = references[check]):
				logger.info('index %s and type %s exist', indexName, references[check])
			else:
				logger.info('index %s exists but type %s does not', indexName, references[check] )
				return False
		return True
	else:
		logger.info('index %s does not exist', indexName)
		return False
