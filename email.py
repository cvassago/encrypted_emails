from ctypes import *
from server import *
import json
from base64 import b64encode, b64decode
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
	print(Fore.MAGENTA + '| Hello! First, enter your email address! If you want to send a message, enter "w". If you want to|')
	print(Fore.MAGENTA + '| read the messages, enter "r".                                                                   |')
	print(Fore.MAGENTA + '|_________________________________________________________________________________________________|')
	print(Style.RESET_ALL)

def getKey():
	f = open('/dev/random', 'rb')
	FEK = f.read(32)
	f.close()
	return FEK

def getN():
	f = open('./emailDB/publickey')
	n = int(f.readline())
	f.close()

	return n

def getRSAKey(login):
	try:
		f = open('./users/' + login + '/secrets/key')
		n = int(f.readline())
		f.close()
	except:
		print(Fore.RED + 'Private key not found!')
		print(Style.RESET_ALL)
		exit()
	return n

def sendMessage(emailFrom):
	emailTo = getEmail() + ' '

	public_key = 0
	while (public_key % 2) == 0:
		if emailTo[-1] == '@':
			print("ERROROROROROROR")
			exit(-1)
		emailTo = emailTo[0:-1]
		print(emailTo)
		emailHash = md5_n(emailTo.encode())[:16]
		public_key = int(emailHash.hex(), 16)

	message = input('Enter message:\n')
	if (len(message) < 1):
		print(Fore.MAGENTA + 'You didn`t enter message. It`s your choice, bye 😈')
		print(Style.RESET_ALL)
		exit()

	key = getKey()
	rsaMagic = pow(int(key.hex(), 16), public_key, getN())
	#print(rsaMagic)
	header = (str(rsaMagic) + '\n' + emailFrom).encode()

	cipher = AES.new(key, AES.MODE_EAX)
	cipher.update(header)
	ciphertext, tag = cipher.encrypt_and_digest(message.encode("utf8"))
	
	json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
	json_v = [ b64encode(x).decode('utf-8') for x in [cipher.nonce, header, ciphertext, tag] ]

	os.makedirs('./users/'+ emailTo.split('@')[0] + '/email', exist_ok=True)
	with open('./users/'+ emailTo.split('@')[0] + '/email/' + '1', 'w') as f:
		json.dump(dict(zip(json_k, json_v)),f)

def readMessages(emailFrom):
	try:
		emails = os.listdir('./users/' + emailFrom.split('@')[0] + '/email/')
	except:
		print(Fore.RED + 'You don\'t have any emails!')
		print(Style.RESET_ALL)
		exit()

	print(Fore.MAGENTA + 'Select the email you want to read')
	print(Style.RESET_ALL)

	for email in emails:
		print(email)
	
	for i in range(len(emails)):
		address = input('Select a message: ')
		try:
			with open('./users/' + emailFrom.split('@')[0] + '/email/' + address, 'r') as f:
				b64 = json.load(f)
			json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
			jv = {k:b64decode(b64[k]) for k in json_k}
			print(jv['header'])
			keyString = jv['header'].decode('utf-8').split('\n')[0]
			key = pow(int(keyString), getRSAKey(emailFrom.split('@')[0]), getN())
			print(key)
			cipher = AES.new(str(key).encode(), AES.MODE_EAX, nonce=jv['nonce'])
			cipher.update(jv['header'])
			plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
			print("The message was: " + plaintext)
		except [ValueError, KeyError]:
			print(Fore.RED + "Incorrect decryption")
			print(Style.RESET_ALL)
			exit()

if __name__ == "__main__":
	helloEmail()
	emailFrom = getEmail()
	readWrite = input('Enter w or r: ')
	if (readWrite == 'w'):
		sendMessage(emailFrom)
	elif (readWrite == 'r'):
		readMessages(emailFrom)
	else:
		print(Fore.MAGENTA + 'You didn`t enter w or r. It`s your choice, bye 😈')
		print(Style.RESET_ALL)
