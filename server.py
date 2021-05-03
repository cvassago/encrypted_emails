import getpass
import ctypes

md5_c = ctypes.CDLL('/home/dasha/University/Crypto/Kursach/code/crypto/md5.so')
md5_c_func = lambda input: md5_c.md5(ctypes.c_char_p(input.encode('utf-8')))

#email = input()
password = getpass.getpass(prompt='Get password: ')

if (password):
	print('pass = ' + password)
	print('hash = ', md5_c_func(password))
else:
	print('No pass')

