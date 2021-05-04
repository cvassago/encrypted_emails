import getpass
from ctypes import *

libcrypto = CDLL('./libcrypto.so')
md5 = libcrypto.md5
md5.argtype = c_char_p
md5.restype = c_char_p

#email = input()
password = getpass.getpass(prompt='Get password: ')

if (password):
	print('pass = ' + password)
	res = md5(password)[:16]
	print('hash = ', res.hex())
else:
	print('No pass')

