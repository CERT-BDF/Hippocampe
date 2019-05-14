# User Guide

## Intro

The following guide will describe how to use *Hippocampe*'s services.
Below the services' list:

+ [distinct](#distinct)
+ [freshness](#freshness)
+ [hipposched](#hipposched)
+ [hipposcore](#hipposcore)
+ [jobs](#jobs)
+ [lastQuery](#lastquery)
+ [lastStatus](#laststatus)
+ [monitorSources](#monitorsources)
+ [more](#more)
+ [new](#new)
+ [schedReport](#schedreport)
+ [shadowbook](#shadowbook)
+ [sizeBySource](#sizebysource)
+ [sizeByType](#sizebytype)
+ [sources](#sources)
+ [type](#type)

 ***

## distinct
*distinct* service takes an intelligence type as parameter, it returns all distinct values that match the type given.
### Example

+ all distinct ip known by *Hippocampe*: 
**Query** :
```
curl -i -H "Content-Type: application/json" -X POST -d '
{
        "field" : ["ip"]
}' http://localhost:5000/hippocampe/api/v1.0/distinct
```
**Response**:
```
{
  "ip": [
    "8.8.8.8",
    "0.0.0.0"
	]
}
```

+ all distinct ip and url known by *Hippocampe*:
**Query**:
```
curl -i -H "Content-Type: application/json" -X POST -d '
{
        "field" : ["ip", "url"]
}' http://localhost:5000/hippocampe/api/v1.0/distinct
```
**Response**:
```
{
  "ip": [
    "8.8.8.8",
    "0.0.0.0"
	],
   "url": [
	"http://www.evil.com/malicious.exe",
	"http://www.evil.com/veryMalicious.exe"
	]
}

```

***

## freshness
*freshness* service checks if your feeds are "up to date".
In ```hippocampe/core/conf/hippo/hippo.conf``` a threshold can be defined, by default it is setted to 1 day:
```
[freshness]
#in days
threshold : 1
```
If the feed has not been querried within the last day, the service returns "NOK", otherwise it returns "OK".
### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/freshness
```

**Response**:
```
{
  "http://autoshun.org/files/shunlist.csv": {
    "freshness": "OK"
  },
  "http://data.phishtank.com/data/online-valid.csv": {
    "freshness": "NOK"
  },
  "http://labs.snort.org/feeds/ip-filter.blf": {
    "freshness": "OK"
  }
```

***

## hipposched
*Hippocampe* retrieves threat intelligence from internet's feed to index it. This is done through [shadowbook](#shadowbook) service.
*hipposched* allows to schedule automaticaly the launch of  [shadowbook](#shadowbook), in other words automatic indexation is possible.
The crontab syntax is used to indicate the job's frequency.
### Example
+ Indexation every 12 hours
**Query**:
```
curl -i -H "Content-Type: application/json" -X POST -d '
{
        "time" : "* */12 * * *"
}' http://localhost:5000/hippocampe/api/v1.0/hipposched
```
**Response**:
```
{
  "schedule": "* */12 * * *"
}
```

Please be aware that: 

+ the scheduling is stored in *memory*, if the API is stopped and started again, another querry has to be sent to schedule jobs
+ yet, there is no way to get the scheduled frequency from the API
    + looking for the string ```job succesfully schedulled as: * */12 * * *``` in the log can be a workaround
+ if a shadowbook job is already running, as a job A, and another one is about to be launched because of *hipposched*, as a job B
    + job B would be launched after the end of job A


***

## hipposcore
*hipposcore* service takes one or several observables as parameters and returns a score for each. 
The score is ranged between 0 and -100:

+ 0 : observable unknown
+ -100: super evil observable

### Example
**Query**:
```
curl -i -H "Content-Type: application/json" -X POST -d '
{
        "perugemstones.com" : {"type" : "domain"},
        "198.23.78.98" : {"type" : "ip"},
        "223.184.173.74" : {"type" : "ip"}
}' http://localhost:5000/hippocampe/api/v1.0/hipposcore

```
**Response**:
```
{
  "198.23.78.98": 0,
  "223.184.173.74": {
    "hipposcore": -86.46647167633873
  },
  "perugemstones.com": {
    "hipposcore": -86.46647167633873
  }
}
```
For more details on the *hipposcore* formula, check [this](hipposcore.md).

***

## jobs
*Hippocampe* retrieves threat intelligence from internet's feed to index it. This is done through [shadowbook](#shadowbook) service. 
At the end of the process, a "report" is generated to sum it up. 
*jobs* service allows to return every report generated.

### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/jobs
```

**Response**:
```
{
  "AVSF_66jpkveE_5U5iuW": {
    "duration": "6.52",
    "endTime": "20160506T142317+0200",
    "report": {
      "ET_IP.conf": {
        "activated": true,
        "error": [],
        "link": "http://rules.emergingthreats.net/blockrules/compromised-ips.txt",
        "nbFailed": 0,
        "nbIndex": 1158,
        "nbNew": 1062,
        "nbUpdate": 0
      },
      "snort_IP.conf": {
        "activated": true,
        "error": [],
        "link": "http://labs.snort.org/feeds/ip-filter.blf",
        "nbFailed": 0,
        "nbIndex": 40365,
        "nbNew": 39841,
        "nbUpdate": 0
      }
    },
    "startTime": "20160506T141646+0200",
    "status": "done"
  }
```

The service returns the jobs which *id* is ```AVSF_66jpkveE_5U5iuW```.

+ *duration* is the time spent in minutes for the indexation
+ *endTime* has the format ```"%Y%m%dT%H%M%S%z"```
+ *report* is a JSON document which each key is the source's configuration file
    + *activated* is a boolean.
If the source is activated, it will be querried. If not, it will not.
    + *error* is a list of string.
In case of failure, the exception name will be indicated in the list.
    + *link* is the source's url.
    + *nbFailed* is the number of failure.
A feed is composed by several lines. Sometimes, the process cannot index some lines. *nbFailed* is the exact number.
    + *nbIndex* is the number of element succesfully indexed.
    + *nbNew* is the number of element not known before by *Hippocampe*. These elements are also indexed under the index/type hippocampe/new.
    + *nbUpdate* is the number of element successfully updated.
When an element is already known, its *lastAppearance* date is updated.
+ *startTime* has the format ```"%Y%m%dT%H%M%S%z"```
+ *status* is the job's status.
    + Yet there's only three statuses: ```ongoing```, ```done``` and ```failed```

***

## lastquery
*lastQuery* returns the last query date for every sources. samedi, 07. mai 2016 03:50 
he date format is ```"%Y%m%dT%H%M%S%z"```
### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/lastQuery
```
**Response**:
```
{
  "http://autoshun.org/files/shunlist.csv": {
    "lastQuery": "20160505T180913+0200"
  }, 
  "http://data.phishtank.com/data/online-valid.csv": {
    "lastQuery": "20160505T180932+0200"
  }
}
```

## laststatus
*lastStatus* service checks if the last indexation went well. It checks the last job report, returns ```OK``` if there's no error and if ```(nbIndexed =! 0 and nbUpdated != 0)```, if not it returns ```NOK```.
### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/lastStatus
```

**Response**:
```
{
  "https://palevotracker.abuse.ch/blocklists.php?download=ipblocklist": {
    "lastStatus": "NOK"
  }
}
```

***
## monitorsources
*monitorSources* service "concatenates" 4 services:

+ [*freshness*](#freshness)
+ [*lastQuery*](#lastquery)
+ [*schedReport*](#schedreport)
+ [*sizeBySource*](#sizebysource)

### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/monitorSources
```
**Response**:
```
{
  "http://autoshun.org/files/shunlist.csv": {
    "freshness": "OK", 
    "lastQuery": "20160505T180913+0200", 
    "schedReport": "NOK", 
    "size": 500
  }, 
  "http://data.phishtank.com/data/online-valid.csv": {
    "freshness": "OK", 
    "lastQuery": "20160505T180932+0200", 
    "schedReport": "NOK", 
    "size": 0
  }, 
  "http://labs.snort.org/feeds/ip-filter.blf": {
    "freshness": "OK", 
    "lastQuery": "20160505T180814+0200", 
    "schedReport": "NOK", 
    "size": 39399
  }
}
```

***

## more
*more* service returns intelligence about an element given in parameters.
### Example
**Query**:
```
curl -i -H "Content-Type: application/json" -X POST -d '
{
        "http://www.mkpoytuyr.com/f/" : {"type" : "url"},
        "199.9.24.1" : {"type" : "ip"},
        "223.184.173.74" : {"type" : "ip"}
}' http://localhost:5000/hippocampe/api/v1.0/more
```
**Response**:
```
{
  "199.9.24.1": [], 
  "223.184.173.74": [
    {
      "firstAppearance": "20160505T180916+0200", 
      "hipposcore": {
        "hipposcore": -98.12798922301901
      }, 
      "idSource": "AVSBria00AEA_f3Kf714", 
      "ip": "223.184.173.74", 
      "lastAppearance": "20160505T180916+0200", 
      "source": "https://feodotracker.abuse.ch/blocklist/?download=ipblocklist"
    }, 
    {
      "firstAppearance": "20160505T180837+0200", 
      "hipposcore": {
        "hipposcore": -98.12798922301901
      }, 
      "idSource": "AVSBrTzd0AEA_f3KfbZ4", 
      "ip": "223.184.173.74", 
      "lastAppearance": "20160505T180837+0200", 
      "source": "http://labs.snort.org/feeds/ip-filter.blf"
    }
  ], 
  "http://www.mkpoytuyr.com/f/": []
}
```
The response is a JSON document. Each key is an observable previously submitted. 
The value associated is a list.
Each element of the list, is a record found in *Hippocampe*'s feed. For instance, ```223.184.173.74``` is seen in ```"https://feodotracker.abuse.ch/blocklist/?download=ipblocklist"``` and in ```"http://labs.snort.org/feeds/ip-filter.blf"```.
When the list is empty, it means that the observable is unknown.

***

## new
*Hippocampe* retrieves threat intelligence from internet's feed to index it.
New intelligences, neve seen before, are also indexed under the index/type hippocampe/new.
*new* service returns all elements under this index/type to search them in your information system.
### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/new
```
**Response**:
```
{
  "AVSBrS-10AEA_f3KfZr-": {
    "toSearch": "http://www.badevil.org/malicious.EXE",
    "type": "url"
  },
  "AVSBrYyN0AEA_f3KfgJi": {
    "toSearch": "14.141.209.194", 
    "type": "ip"
  }
}
```

***

## schedreport
With [*hipposched*](#hipposched) service, indexation can be scheduled.
If the indexation is scheduled every 12 hours, *schedReport* checks if an indexation has been launched in the last 12 hours. If so, it returns ```OK```, if not it returns ```NOK``` for every sources.
The threshold is defined in ```hippocampe/core/conf/hippo/hippo.conf```:
```
[schedReport]
#in hours 
threshold: 12
```
### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/schedReport

```
**Response**:
```
{
  "http://malwareurls.joxeankoret.com/normal.txt": {
    "schedReport": "OK"
  }
}
```

***

## shadowbook
When launched, *shadowbook* service retrieves feeds from internet to index them. 
Feeds to be requested are indicated under ```hippocampe/core/conf/feeds```. 
Check [this](how_to_add_feed.md) for more details on how to add feed.

### Example
**Query**:
```
curl -XGET localhost:5000/hippocampe/api/v1.0/shadowbook

```
**Response**:
```
{
  "job": {
    "AVSQjAYZGLawP2pF8zFV": "ongoing"
  }
}
```
The response precises the job's id (```AVSQjAYZGLawP2pF8zFV```) and the status (```ongoing```).
Please note that there is only one *ongoing* job at a time. If the service is requested while it is indexing, the request would not be processed and the following response would be returned:
```
{
  "error": "Ongoing job already running"
}
```

***

## sizebysource
*sizeBySource* service returns  the size's source (number of element) for every sources.

### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/sizeBySources
```

**Response**:
```
{
  "http://autoshun.org/files/shunlist.csv": {
    "size": 500
  }, 
  "http://labs.snort.org/feeds/ip-filter.blf": {
    "size": 40838
  }
}
```

***

## sizebytype

*sizeByType* service returns  the number of element for each observable's type.

### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/sizeByType

```

**Response**:
```
{
  "domain": {
    "size": 31050
  }, 
  "ip": {
    "size": 186848
  }, 
  "url": {
    "size": 8323
  }
}
```

***

## sources
*sources* service returns every feed's sources known and theirassociated metadata.

### Example
**Query**:
```
curl -GET http://localhost:5000/hippocampe/api/v1.0/sources

```

**Response**:
```
{
  "http://autoshun.org/files/shunlist.csv": {
    "coreIntelligence": "ip",
    "description": "AutoShun is a Snort plugin that allows you to send your Snort IDS logs to a centralized server that will correlate attacks from your sensor logs with other snort sensors, honeypots, and mail filters from around the world. The input from your logs will be used to identify hostile address that are bots, worms, spam engines which we use to build a shun list.",
    "firstQuery": "20160508T201602+0200",
    "lastQuery": "20160508T201602+0200",
    "link": "http://autoshun.org/files/shunlist.csv",
    "score": -100,
    "type": "autoshunFree_shunlistIP"
  },
  "http://data.phishtank.com/data/online-valid.csv": {
    "coreIntelligence": "url",
    "description": "PhishTank is a collaborative clearing house for data and information about phishing on the Internet",
    "firstQuery": "20160508T201617+0200",
    "lastQuery": "20160508T201617+0200",
    "link": "http://data.phishtank.com/data/online-valid.csv",
    "score": -100,
    "type": "phishtankFree_onlinevalidURL"
  },
  "http://labs.snort.org/feeds/ip-filter.blf": {
    "coreIntelligence": "ip",
    "description": "IP blacklist from labs.snort.org which is an undertaking by the Sourcefire VRT.",
    "firstQuery": "20160508T201511+0200",
    "lastQuery": "20160508T201511+0200",
    "link": "http://labs.snort.org/feeds/ip-filter.blf",
    "score": -100,
    "type": "snortFree_filterIP"
  }
}
```

The response is a JSON doc which each keys are source's urls.
The values associated to the key are the matadata:

+ *coreIntelligence* is the observable's type found in the feed
+ *description* is a short description of the feed
+ *firstQuery* is the first querried date of the feed
+ *lastQuery* is the last querried date of the feed
+ *link* is the feed's url
+ *score* is the feed's score of confidence
+ *type* is the elasticsearch's type under wich the intelligences are stored

***
 
## type
*type* service returns every observable's type available in *Hippocampe*.

### Example
**Query**:
```
curl -XGET localhost:5000/hippocampe/api/v1.0/type

```

**Response**:
```
{
  "type": [
    "ip", 
    "domain", 
    "url"
  ]
}
```
