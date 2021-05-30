from ctypes import *
from server import *
import json
from base64 import b64encode
from Crypto.Cipher import AES

libcrypto = CDLL('./libcrypto.so')
md5_n = libcrypto.md5
md5_n.argtype = c_char_p
md5_n.restype = c_char_p

def helloEmail():
	print(Fore.GREEN +  '____ _  _ ____ _ _     _  _ _   _ ')
	print(Fore.GREEN +  '|___ |\/| |__| | |     |\/|  \_/  ')
	print(Fore.GREEN +  '|___ |  | |  | | |___ .|  |   |   ')
	print(Style.RESET_ALL)

	print(Fore.MAGENTA + '___________________________________________________________________________________________________')
	print(Fore.MAGENTA + '|                                                                                                 |')
	print(Fore.MAGENTA + '| Hello! If you want to send a message, enter "w". If you want to read the messages, enter "r".   |')
	print(Fore.MAGENTA + '|_________________________________________________________________________________________________|')
	print(Style.RESET_ALL)

def getKey():
	f = open('/dev/random', 'rb')
	FEK = f.read(32)
	f.close()
	#return FEK
	return int(FEK.hex(), 16)

def getN():
	f = open('./emailDB/publickey')
	n = int(f.readline())
	f.close()

	return n

def sendMessage():
	email = getEmail() + ' '

	public_key = 0
	while (public_key % 2) == 0:
		if email[-1] == '@':
			print("ERROROROROROROR")
			exit(-1)
		email = email[0:-1]
		print(email)
		emailHash = md5_n(email.encode())[:16]
		public_key = int(emailHash.hex(), 16)

	message = input('Enter message:\n')
	if (len(message) < 1):
		print(Fore.MAGENTA + 'You didn`t enter message. It`s your choice, bye 😈')
		print(Style.RESET_ALL)
		exit()

	key = bytes(getKey())
	n = getN()
	header = b'ytes((int(key) ** int(public_key)) % n)'

	cipher = AES.new(key, AES.MODE_EAX)
	cipher.update(header)
	ciphertext, tag = cipher.encrypt_and_digest(message)
	
	json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
	json_v = [ b64encode(x).decode('utf-8') for x in [cipher.nonce, header, ciphertext, tag] ]

	os.makedirs('./users/'+ email.split('@')[0] + '/email', exist_ok=True)
	with open('./users/'+ email.split('@')[0] + '/email/' + '1', 'w') as f:
		result = json.dumps(dict(zip(json_k, json_v)), f)
		print(result)

	#rsaMagic = bytes((int(key) ** int(public_key)) % n)
	#print(rsaMagic)

if __name__ == "__main__":
	helloEmail()
	readWrite = input('Enter w or r: ')
	if (readWrite == 'w'):
		sendMessage()
	elif (readWrite == 'r'):
		print()
	else:
		print(Fore.MAGENTA + 'You didn`t enter w or r. It`s your choice, bye 😈')
		print(Style.RESET_ALL)
