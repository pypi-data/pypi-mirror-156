
import time
from aiohttp_session import get_session
from appPublic.rsa import RSA
from appPublic.rc4 import KeyChain

crypted_data_dic = {}

def get_remote_addr(request):
	r = request.headers.get('X-Forwarded-For')
	if r:
		return r
	return request.remote

def get_cd(request):
	remote = get_remote_addr(request)
	d = crypted_data_dic.get(request.remote)
	if cd:
		t = time.time()
		d['last_time'] = t
		return d['cd']
	return None

def set_cd(remote, cd):
	t = int(time.time())
	d = {
		'last_time':t,
		'cd':cd
	}
	crypted_data_dic[remote] = d

class CryptedData:
	def __init__(self, remote, pubkey, secret_book):
		self.remote = remote
		self.peer_pubkey = pubkey
		self.keychain = KeyChain(secret_book)
		self.prikey = 

	def decode(self, request, data):
		pass

	def encode(self, request, data):
		
