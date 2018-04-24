import time
from kazoo.client import KazooClient
import sys 
from os.path import dirname, abspath
import json
import pprint

class Zooconf:
	__zkcon = None
	__serviceConfig = None
	__fsList = None
	
	def __init__(self):
		sys.stderr.write("Fileservicepython start initialization at " + str(int(round(time.time() * 1000))))
		sys.stderr.flush()
		
		self.__initConfProperties()
		self.__zooConnect()
		self.__publishService()
		self.__initFsWatches();
        

	def __initConfProperties(self):
		sys.stderr.write(dirname(dirname(abspath(__file__))))
		sys.stderr.flush()
		self.__serviceConfig = dict()
		
		with open(dirname(dirname(abspath(__file__)))+"/config.properties", 'r') as f:
			for line in f:
				line = line.rstrip()

				if "=" not in line: 
					continue #skips blanks and comments w/o =
				if line.startswith("#"): 
					continue #skips comments which contain =
				k, v = line.split("=", 1)
				self.__serviceConfig[k] = v
			f.close() 
			
	def __zooConnect(self):
		sys.stderr.write("Start zooconnect")
		sys.stderr.flush()
		
		config = self.getServiceConfig();
		
		self.__zkcon = KazooClient(hosts=config["ZOOKEEPER_HOST"])
		self.__zkcon.start()
		digest_auth = "%s:%s" % (config["ZOOKEEPER_USER"], config["ZOOKEEPER_PASSWORD"])
		self.__zkcon.add_auth("digest", digest_auth)
		
	def __initFsWatches(self):
		# lists are supposed to be thread safe in python
		self.__fsList = []
		@self.__zkcon.ChildrenWatch("/plh414python/fileservices")
		def watch_children(children):
			self.__fsList = []
			sys.stderr.write("Children are now: %s" % children)
			sys.stderr.flush()
			for child in children:
				self.__fsList.append(child)
		# Above function called immediately, and from then on
		
	def __publishService(self):
		from kazoo.security import make_digest_acl
		config = self.getServiceConfig();
		acl = make_digest_acl(config["ZOOKEEPER_USER"], config["ZOOKEEPER_PASSWORD"], all=True)
		
		dataJsonDict = {}
		dataJsonDict['SERVERHOSTNAME'] = config["SERVERHOSTNAME"]
		dataJsonDict['SERVER_PORT'] = config["SERVER_PORT"]
		dataJsonDict['SERVER_SCHEME'] = config["SERVER_SCHEME"]
		dataJsonDict['CONTEXT'] = config["CONTEXT"]
		
		self.__zkcon.set("/plh414python/directoryservice/", json.JSONEncoder().encode(dataJsonDict).encode(), -1)

	def getAvailableFs(self):
		return self.__fsList;
	
	def getZooConnection(self):
		return self.__zkcon

	def getServiceConfig(self):
		return self.__serviceConfig

#imported only once per module
zk = Zooconf()
