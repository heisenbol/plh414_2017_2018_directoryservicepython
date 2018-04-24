#!/usr/bin/python3
# -*- coding: UTF-8 -*-# enable debugging


import os
import os.path
from pathlib import Path
import sys 
os.chdir(os.path.dirname(__file__))
# so I can load custom modules
sys.path.append(os.path.dirname(__file__))
import bottle
import bcrypt
import time
from Crypto.Cipher import AES
from Crypto import Random
from base64 import b64decode
import hmac
import hashlib
import urllib.parse

import json
# zk is defined as instance of Zooconf class
from tuc.zoo import zk
from bottle import route, run, template, response, redirect

application = bottle.default_app()
# we do not need session for the file service
#application = beaker.middleware.SessionMiddleware(bottle.default_app(), session_opts)
sys.stderr.write("Directoryservice python start process at " + str(int(round(time.time() * 1000))))
sys.stderr.flush()

# do not cache templates
bottle.debug(True)	

@route('/status')
def status():
	sys.stderr.write("Python Directory Service status called ")
	sys.stderr.flush()
	response.content_type = 'text/plain; charset=utf-8'
	
	return ["alive \n"+getStatusText() ]
	

def getStatusText():
	result = ""
	rootPath = "/plh414python"
	zkCon = zk.getZooConnection()
	
	
	
	
	authChildren = zkCon.get_children(rootPath+"/authservices")
	fsChildren = zkCon.get_children(rootPath+"/fileservices")
	dsDataBytes, stat = zkCon.get(rootPath+"/directoryservice");
	result = "Directoryservice data: "+ dsDataBytes.decode("utf-8")+"\n";

	for auth in authChildren:
		authDataBytes, stat = zkCon.get(rootPath+"/authservices/"+auth)
		result = result + "Auth data for "+auth+": "+ authDataBytes.decode("utf-8")+"\n"

	result = result + "\nFS List retrieved now\n";
	for fs in fsChildren:
		fsDataBytes, stats = zkCon.get(rootPath+"/fileservices/"+fs)
		result = result + "FS data for "+fs+": "+ fsDataBytes.decode("utf-8")+"\n"

	result = result + "\nFS List names according to watched list\n "
	for fs in zk.getAvailableFs():
		result = result + fs+", ";


	return result;
	

