import os
import base64
import uuid
import hashlib
import hmac
import json
from time import time
from requests import Session
from .exc import CheckExceptions
class Client:
	def __init__(self,device:str=None):
		if device is not None:
			self.device = device
		else:
			self.device = self.deviceId()
		self.req = Session()
		self.uuid = str(uuid.uuid4())
		self.api = "https://service.narvii.com/api/v1"
		self.headers = {"NDCDEVICEID":self.device,
		"SMDEVICEID":self.uuid,
		"Accept-Language":"en-EN",
		"Content-Type": "application/json; charset=utf-8",
		"User-Agent":"Dalvik/2.1.0 (Linux; U; Android 7.1.2; vmos Build/NZH54D; com.narvii.amino.master/3.5.34180)"
		,"Host":"service.narvii.com","Accept-Encoding":"gzip",
		"Connection":"Keep-Alive"}
		self.sid = None
		self.userId = None
	
	def deviceId(self):
		urandom = os.urandom(20)
		return ("42" + urandom.hex() + hmac.new(bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F"), b"\x42" + urandom, hashlib.sha1).hexdigest()).upper()
		
	def sig(self,data):
		return base64.b64encode(bytes.fromhex("42") + hmac.new(bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93"), data.encode("utf-8"),hashlib.sha1).digest()).decode("utf-8")
	
	def login(self,email:str,password:str):
		data = json.dumps(
		{"email": email,"secret": f"0 {password}","deviceID": self.device,"clientType": 100, "action": "normal","timestamp": (int(time() *1000))})
		self.headers["NDC-MSG-SIG"] = self.sig(data)
		req = self.req.post(f"{self.api}/g/s/auth/login",headers=self.headers,data=data)
		if req.status_code!=200:
			return CheckExceptions(req.json())
		self.sid = req.json()["sid"]
		self.userId = req.json()["auid"]
		return req.json()