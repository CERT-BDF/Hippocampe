#!/usr/bin/env python
# -*- coding: utf8 -*-


from modules.more.ObjToEnrich import ObjToEnrich
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count, Queue
from ES import getES
from hipposcore import calcHipposcore 
nbProcessPerCPU = 1 
import logging
logger = logging.getLogger(__name__)

def tellMeMore(chunkedList):
	chunkedDict = dict(chunkedList)
	result = dict()
        for ioc, attributes in chunkedDict.items():
                objIoc = ObjToEnrich(attributes['type'], ioc)
		try:
                	result[ioc] = objIoc.getDetails() 
		except Exception as e:
			logger.error('tellMeMore failed, no idea where it came from', exc_info = True)
			result[ioc] = dict()
			result[ioc]['error'] = str(e)
        return result

def main(jsonRequest):
	logger.info('more.main launched')
	logger.info(jsonRequest)
	#dictionnary that contains the response
	response = dict()
	
	#the client-request (JSON dict) has to be converted into a list
	#Indeed, in order to "multi-threaded" the process
	#pool.map will iterate on the argument
	#however, iterate on a dict gives only the key (which is unicode type)
	#whereas dict type is needed to tellMeMore
	#a list of dict is therefore the solution
	items = list(jsonRequest.items())
	
	#the client-request list (items variable) will be splited into n small
	#requests which included chunksize elements
	chunksize = 10	
	
	#cutting the items list into several small ones with chunksize length	
	chunks = [items[i:i + chunksize] for i in range(0, len(items), chunksize)]
	
	pool_size = cpu_count() * nbProcessPerCPU
	pool = ThreadPool(processes=pool_size)
	queue = Queue()
	
	#updating directly response dict causes errors
	#that's why result from tellMeMore function is queued
	#logger.info('beginning tellMeMore with several threads')
	queue.put(pool.map(tellMeMore, chunks))

	#gathering all result from the queue into one dict
	for element in queue.get():
		response.update(element)
	
	pool.close()
	pool.join()
	#logger.info('tellMeMore.main pool closed and joined')

	#yet, the response does not include hipposcore
	#let's add the hipposcore to the response
	#let's fix their broken bullshit too!
	logger.warning("initiating fix")

	try:
		new_response = {}
		for ip, data in response.iteritems():
			temp_list = []
			for item in data:
				if item["idSource"] == '':
					item["idSource"] = fixThisBrokenBullshit(item["source"])
				temp_list.append(item)
			new_response[ip] = temp_list
	except Exception as e:
		logger.error('failed to fix their broken shit', exc_info = True)
		logger.error(response)
		report = dict()
		report['error'] = str(e)

	hipposcoreDict = calcHipposcore(new_response)

	#two dicts, response with all data
	#{u'103.16.26.228': [{u'date': u'20151001T112643+0200',
	#                     u'firstAppearance': u'20151001T112643+0200',
	#                     u'idSource': u'AVAiuZ7ADAiil8mrVC0p',
	#                     u'ip': u'103.16.26.228',
	#                     u'lastAppearance': u'20151001T112643+0200',
	#                     u'source': u'abuseFree_feodotrackerIP'}],
	# u'103.16.26.36': [{u'date': u'20151001T112643+0200',
	#                    u'firstAppearance': u'20151001T112643+0200',
	#                    u'idSource': u'AVAiuZ7ADAiil8mrVC0p',
	#                    u'ip': u'103.16.26.36',
	#                    u'lastAppearance': u'20151001T112643+0200',
	#                    u'source': u'abuseFree_feodotrackerIP'}],
	# u'199.9.24.1': [],
	# u'datingzzzj.ru': [],
	# u'trkl.su': []}

	#hipposcoreDict with only hipposcore
#	{u'103.16.26.228': {'hipposcore': -86.46647167633873},
#	 u'103.16.26.36': {'hipposcore': -86.46647167633873},
#	 u'199.9.24.1': 0,
#	 u'datingzzzj.ru': 0,
#	 u'trkl.su': 0}

	for keyRes, listMatch in response.items():
		for keyScore, scoreDict in hipposcoreDict.items():
			if keyRes == keyScore:
				for match in listMatch:
					match['hipposcore'] = scoreDict
	logger.info('more.main end')
	return response

def fixThisBrokenBullshit(source):
	es = getES()

	data = {
		'query' : {
			'bool' : {
				'must' : [
					{'match' : {'source' : source}}
					]
				}
			}
		}

	res = es.search(body=data)

	for i in res['hits']['hits']:
		if i["_source"]["idSource"] != "":
			return i["_source"]["idSource"]
			break
		else:
			continue


if __name__ == '__main__':
	main()
