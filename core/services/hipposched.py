#!/usr/bin/env python
# -*- coding: utf8 -*-


from apscheduler.schedulers.background import BackgroundScheduler
import shadowbook
import logging
import os

os.environ['TZ']= 'America/New_York'

logger = logging.getLogger(__name__)
def main(request):
	logger.info('hipposched.main launched')
	try:
		jobId = 'shadowbook'
		time = request['time']
		logger.info('schedule submitted as: ' + str(time))
		#processing time to isolate each field
		tabTime = time.split(' ')
		#tabTime
		#	[0] min
		#	[1] hour
		#	[2] day of month
		#	[3] month
		#	[4] day of week
		sched = BackgroundScheduler()
		#always erase the previous schedule
		#because of replace_existing = True
		#logger.info('creating job')
		sched.add_job(shadowbook.hipposchedVersion,
			'cron',
			minute = tabTime[0],
			hour = tabTime[1],
			day = tabTime[2],
			month = tabTime[3],
			day_of_week = tabTime[4],
			replace_existing = True,
			id = jobId)
		sched.start()
		logger.info('job succesfully schedulled as: ' + str(time))
		report = dict()
		report['schedule'] = time
		logger.info('hipposched.main end')
		return report
	except Exception as e:
		logger.error('hipposched.main failed, no idea where it came from', exc_info = True)
		report = dict()
		report['error'] = str(e)
		return report


