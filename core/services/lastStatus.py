#!/usr/bin/env python
# -*- coding: utf8 -*-


from modules.jobs.BagOfJobs import BagOfJobs
import logging
logger = logging.getLogger(__name__)

def main():
	logger.info('lastStatus.main launched')
	try:
		result = dict()
		bag = BagOfJobs()
		globalReport = bag.getLastJob()
		for confFileName, report in globalReport['report'].items():
			if 'link' in report: result[report['link']] = dict()
			if report['error']:
				#there's one or more errors
				result[report['link']]['lastStatus'] = 'NOK'
			elif report['nbIndex'] == 0 and report['nbUpdate'] == 0:
				#the feed might have not been downloaded
				result[report['link']]['lastStatus'] = 'NOK'
			else:
				result[report['link']]['lastStatus'] = 'OK'
		logger.info('lastStatus.main end')
		return result
	except Exception as e:
		logger.error('lastStatus.main failed, no idea where it came from...', exc_info = True)
		report = dict()
		report['error'] = str(e)
		return report
