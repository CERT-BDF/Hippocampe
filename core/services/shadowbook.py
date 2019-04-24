#!/usr/bin/env python
# -*- coding: utf8 -*-


"""
	This module contains the shadowBook process.
"""
from modules.shadowbook import createSessions
from modules.common import getConf
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Queue
import os
from os import listdir
from os.path import join
from functools import partial
from modules.shadowbook import processFeed
from traceback import print_exc
import logging
logger = logging.getLogger(__name__)

from modules.shadowbook.objects.IndexJob import IndexJob
from modules.shadowbook.objects.Job import Job
from time import sleep
def startJob():
	logger.info('shadowbook.startJob launched')
	try:
		#creating sessions for feeds which need authentification
		listSessions = createSessions.createSessions()

		#retrieving the config from hippo.conf file
		cfg = getConf.getHippoConf()
		nbThreadPerCPU = cfg.getint('shadowbook', 'nbThreadPerCPU')

		#processFeed needs 2 parameters:
        	#       * the conf path
        	#       * the listSessions
        	#processIoc is launched in a multithreaded way
        	#However pool.map does not handle multiple arguments
        	#we use functools.partial to bypass this limitation
		pool_size = cpu_count() * nbThreadPerCPU
		pool = ThreadPool(processes=pool_size)
		queue = Queue()
		
		#json which reports the result from all feeds
		reportAllFeeds = dict()
		#arguments must be in a list
		argInputs = list()
		feedsPath = os.path.dirname(os.path.abspath(__file__)) + '/../conf/feeds'
		logger.info(feedsPath)
		
		#building the list which each element is a feedConfPath
		for cfgFile in listdir(feedsPath):
			cfgPath = join(feedsPath, cfgFile)
			logger.info(cfgPath)
			argInputs.append(cfgPath)
		
		for link in argInputs:
			reportAllFeeds.update(processFeed.main(listSessions, link))

		#func = partial(processFeed.main, listSessions)
		#queue.put(pool.map(func, argInputs))
		#pool.close()
		#pool.join()
		#for reportOneFeed in queue.get():
		#	reportAllFeeds.update(reportOneFeed)
		logger.info('shadowbook.startJob end')
		return reportAllFeeds
	except Exception as e:
		logger.info('shadowbook.startJob failed, no idea where it came from...', exc_info = True)
		report = dict()
		report['error shadowbook'] = str(e)
		return report

def initJob():
	logger.info('shadowbook.initJob launched')
	try:
		indexJob = IndexJob()
		#create index/type hippocampe/shadowbookJobs only if it does not exist
		indexJob.createIndexJob()
		job = Job()
		nbOngoingJob = job.searchOngoingJob()
		logger.info('number ongoing job: %s', nbOngoingJob)

		report = dict()
		if nbOngoingJob == 1:
			#only 1 shadowbook job at a time
			report['error'] = 'Ongoing job already running'
			logger.error(report['error'])
		elif nbOngoingJob == 0:
			#create a document in ES which represents a JOB
			#index with a  ongoing status & startTime as <now>
			idJob = job.indexOngoingJob()
			report = dict()
			report['job'] = dict()
			report['job'][idJob] = 'ongoing'
		logger.info(report)
		logger.info('shadowbook.initJob end')
		return report
	except Exception as e:
		logger.error(str(e), exc_info = True)

def updateJob(report, status):
	logger.info('shadowbook.updateJob launched')
	logger.info('updating with status: %s', status)
	#update job status, add the report and calculates the duration
	job = Job()
	job.updateStatus(report, status)
	logger.info('shadowbook.updateJob end')

def manageJob():
	logger.info('shadowbook.manageJob launched')
	#index feeds and update the job's status
	report = startJob()
	if 'error shadowbook' in report:
		status = 'failed'
	else:
		status = 'done'
	updateJob(report, status)
	logger.info('shadowbook.manageJob end')

def hipposchedVersion():
	logger.info('shadowbook.hipposchedVersion launched')
	#special version for the scheduler
	jobDone = False
	while jobDone == False:
		report = initJob()
		if not 'error' in report:
			manageJob()
			jobDone = True
		else:
			#one shadowbook job is already running 
			#wait for 1 minute and try to launch another one if possible
			sleep(60)
	logger.info('shadowbook.hipposchedVersion end')
	
if __name__ == '__main__':
	main()
