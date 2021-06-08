from colorama import Fore, Style
from ctypes import *
from hashlib import md5
import getpass
import sqlite3
import os
import re
from Crypto.Util import number
import sys
from random import randint
from Crypto.PublicKey.RSA import RsaKey, generate
from sympy.ntheory.factor_ import totient

libcrypto = CDLL('./libcrypto.so')
md5_n = libcrypto.md5
md5_n.argtype = c_char_p
md5_n.restype = c_char_p

def helloServer():
	print(Fore.GREEN + '_______ _______ _______ _______ _______ _______      _______ _______ _______ _    _ _______ _______')
	print(Fore.GREEN + '|______ |______ |       |_____/ |______    |         |______ |______ |_____/  \  /  |______ |_____/')
	print(Fore.GREEN + '______| |______ |______ |    \_ |______    |         ______| |______ |    \_   \/   |______ |    \_')
	print(Style.RESET_ALL)

def infoAboutPassword():
	print(Fore.MAGENTA + '___________________________________________________________________________________________________')
	print(Fore.MAGENTA + '|                                                                                                 |')
	print(Fore.MAGENTA + '| Be careful! You don`t have to enter the password, but you won`t be able to get the private key  |')
	print(Fore.MAGENTA + '| if you lose it.                                                                                 |')
	print(Fore.MAGENTA + '|_________________________________________________________________________________________________|')
	print(Style.RESET_ALL)

def checkEmail(email):
	if (len(email) > 32):
		print(Fore.RED + 'Your email is longer than 32 characters! Please try again!')
		print(Style.RESET_ALL)
		return False
	if (bool(re.match('^[a-z0-9@._-]+$', email)) == False):
		print(Fore.RED + 'Your email contains invalid characters! Please try again!')
		print(Style.RESET_ALL)
		return False
	if ('@' not in email and '.' not in email):
		print(Fore.RED + 'Your email doesn`t have a domain! It must be email.my! Please try again!')
		print(Style.RESET_ALL)
		return False
	allEmailList = email.split('@')
	if (len(allEmailList) > 2):
		print(Fore.RED + 'Your email has a lot of @! It must be email.my! Please try again!')
		print(Style.RESET_ALL)
		return False
	if (len(allEmailList[0]) == 0):
		print(Fore.RED + 'Your email doesn`t have a login! Please try again!')
		print(Style.RESET_ALL)
		return False
	if (len(allEmailList[1]) < 3 or '.' not in allEmailList[1]):
		print(Fore.RED + 'Your email has invalid domain! Please try again!')
		print(Style.RESET_ALL)
		return False
	for part in allEmailList[1].split('.'):
		if (len(part) < 1):
			print(Fore.RED + 'Your email has invalid domain! Please try again!')
			print(Style.RESET_ALL)
			return False
	if allEmailList[1] != 'email.my':
		print(Fore.RED + 'Your email has invalid domain! It must be email.my! Please try again!')
		print(Style.RESET_ALL)
		return False
	
	return True

def getEmail():
	for i in range(3):
		email = input('Get email: ')
		if (checkEmail(email)):
			break
		if (i == 2):
			print(Fore.RED + 'You lose!')
			print(Style.RESET_ALL)
			exit()
	return email

def connectToUsersDataBase():
	if os.path.isfile('./serverDB/users.db') == False:
		with open('./serverDB/users.db', 'w', encoding='utf-8') as f:
			pass

	conn = sqlite3.connect('./serverDB/users.db')
	cur = conn.cursor()

	cur.execute("""CREATE TABLE IF NOT EXISTS users(
					userid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
					email TEXT UNIQUE,
					passwordHash TEXT,
					privateKey TEXT,
					publicKey TEXT
					);
				""")
	cur.execute("""CREATE TABLE IF NOT EXISTS domain(
					infoid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
					domain TEXT UNIQUE,
					p TEXT,
					q TEXT
					);
				""")

	conn.commit()
	return conn

def checkPassword(cur, email):
	for i in range(3):
		password = getpass.getpass(prompt='Get password: ')
		passwordHash = md5_n(password.encode())[:16]
		if (str(passwordHash.hex()) == cur.execute('SELECT passwordHash FROM users WHERE email=?', [email]).fetchone()):
			break
		else:
			print(Fore.RED + "Uncorrect password!")
			print(Style.RESET_ALL)
		if (i == 2):
			print(Fore.RED + 'You lose! Uncorrect password! Go out!')
			print(Style.RESET_ALL)
			exit()

def sendKeys(cur, email, domain):
	login = email.split('@')[0]

	keys = cur.execute('SELECT privateKey, publicKey FROM users WHERE email=?', [email]).fetchone()
	n = int(cur.execute('SELECT p FROM domain WHERE domain=?', [domain]).fetchone()[0]) * \
			int(cur.execute('SELECT q FROM domain WHERE domain=?', [domain]).fetchone()[0])
	print('PrivateKey\n{', keys[0], ', ', n, '}\n')
	print('PublicKey\n{', keys[1], ', ', n, '}')
	os.makedirs('./users/'+ login + '/secrets', exist_ok=True)
	with open('./emailDB/publickey', 'w') as f:
		f.write(str(n))
	if keys[0]:
		with open('./users/'+ login + '/secrets/key', 'w') as f:
			f.write(keys[0])
	exit()

if __name__ == "__main__":
	helloServer()
	email = getEmail() + ' '
	domain = email[0:-1].split('@')[1]
	infoAboutPassword()

	public_key = 0
	while (public_key % 2) == 0:
		if email[-1] == '@':
			print("ERROROROROROROR")
			exit(-1)
		email = email[0:-1]
		print(email)
		emailHash = md5_n(email.encode())[:16]
		public_key = int(emailHash.hex(), 16)

	password = getpass.getpass(prompt='Get password: ')
	if (not password):
		print(Fore.MAGENTA + 'You didn`t enter a password. It`s your choice, then don`t complain 😈')
		print(Style.RESET_ALL)
	else:
		passwordHash = md5_n(password.encode())[:16]

	conn = connectToUsersDataBase()
	cur = conn.cursor()

	if (email not in cur.execute('SELECT email FROM users').fetchall()):
		if (domain not in cur.execute('SELECT domain FROM domain').fetchall()):
			pq = []
			while len(pq) != 2:
				x = number.getPrime(randint(129,512)) * 2 + 1
				if number.isPrime(x):
					pq.append(x)
			cur.execute("""INSERT INTO domain(domain, p, q) VALUES(?, ?, ?) ON CONFLICT DO NOTHING;""",
							[domain, str(pq[0]), str(pq[1])])
			conn.commit()
		if (password):
			n = (int(cur.execute('SELECT p FROM domain WHERE domain=?', [domain]).fetchone()[0]) - 1) * \
				(int(cur.execute('SELECT q FROM domain WHERE domain=?', [domain]).fetchone()[0]) - 1)
			p = int(cur.execute('SELECT p FROM domain WHERE domain=?', [domain]).fetchone()[0])
			q = int(cur.execute('SELECT q FROM domain WHERE domain=?', [domain]).fetchone()[0])
			fi = ((p - 1) >> 1) * ((q - 1) >> 1)
			d = pow(int(emailHash.hex(), 16), fi - 1, n)
			cur.execute("""INSERT INTO users(email, passwordHash, privateKey, publicKey) VALUES(?, ?, ?, ?) ON CONFLICT DO NOTHING;""",
							[email, str(passwordHash.hex()), str(d), str(emailHash.hex())])
			conn.commit()
		else:
			cur.execute("""INSERT INTO users(email, passwordHash, privateKey, publicKey) VALUES(?, ?, ?, ?) ON CONFLICT DO NOTHING;""",
							[email, None, None, str(emailHash.hex())])
			conn.commit()
		sendKeys(cur, email, domain)
	else:
		if (password):
			checkPassword(cur, email)
			sendKeys(cur, email, domain)
		else:
			if (cur.execute('SELECT passwordHash FROM users WHERE email=%s', [email]).fetchone() != None):
				print(Fore.GREEN +  'If you want to get the keys, enter the password!')
				print(Style.RESET_ALL)
				if (input('Do you want to get keys? [yes/no] ') == 'yes'):
					checkPassword(cur, email)
					sendKeys(cur, email, domain)
			else:
				print(Fore.RED + 'We warned you, without a password, we will not give you the private key! Go out!')
				print(Style.RESET_ALL)

	conn.close()
