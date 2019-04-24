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
from getConf import getHippoConf
from IndexSource import IndexSource
from time import strftime
import logging
logger = logging.getLogger(__name__)
import dateutil.parser

class Job(ObjToIndex):

	def __init__(self):
		super(Job, self).__init__()
		cfg = getHippoConf()
		self.indexNameES = cfg.get('elasticsearch', 'indexNameES')
		self.typeNameES = cfg.get('elasticsearch', 'typeNameESJobs')
		self.status = str()
		self.startTime = str()
		self.endTime = str()
		self.duration = str()
		self.report = dict()

	def forgeDocSearchOngoing(self):
		"""
			Forges the search query to search source in elasticsearch.
		"""
		self.docSearch = {
		    "query": {
		        "bool": {
		            "must": [
		                {
		                    "match": {
		                        "status": "ongoing"
		                    }
		                }
		            ]
		        }
		    }
		}


	def forgeDocIndexOngoing(self):
		self.docIndex = {
		    "status": "ongoing",
		    "startTime": strftime("%Y%m%dT%H%M%S%z"),

		}

	def forgeDocUpdateJob(self):
		self.docUpdate = {
		    "script": {
				"lang": "painless",
				"source": "ctx._source.status = params.status; ctx._source.endTime = params.endTime; ctx._source.duration = params.duration; ctx._source.report = params.report",
		    	"params": {
		        	"status": self.status,
		        	"endTime": self.endTime,
		        	"duration": self.duration,
		        	"report": self.report,
		    	}
			}
		}

	def searchOngoingJob(self):
		self.forgeDocSearchOngoing()
		nbOngoingJob = self.search()
		return nbOngoingJob

	def indexOngoingJob(self):
		self.forgeDocIndexOngoing()
		self.indexInES()
		return self.idInES

	def getStartTime(self):
		self.searchOngoingJob()
		#self.resSearch looks like:
		#{u'hits': {u'hits': [{u'_score': 11.907724, u'_type': u'jobs', u'_id': u'AVQkDgNs5CYfHJgxlSLE', u'_source': {u'status': u'ongoing', u'startTime': u'20160417T134938+0200'}, u'_index': u'hippocampe'}], u'total': 1, u'max_score': 11.907724}, u'_shards': {u'successful': 5, u'failed': 0, u'total': 5}, u'took': 1, u'timed_out': False}
		startTime = self.resSearch['hits']['hits'][0]['_source']['startTime']
		return startTime

	def calcDuration(self):
		self.startTime = self.getStartTime()
		duration = dateutil.parser.parse(self.endTime) - dateutil.parser.parse(self.startTime)
		#duration in seconds
		duration = duration.total_seconds()
		#duration in minutes
		duration = duration / 60.0
		#limiting to 2 digits
		self.duration = "%.2f" % duration

	def updateStatus(self, report, status):
		self.endTime = strftime("%Y%m%dT%H%M%S%z")
		self.status = status
		self.report = report

		self.calcDuration()
		self.forgeDocUpdateJob()
		self.update()
