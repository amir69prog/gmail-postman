import smtplib
from abc import ABC, abstractmethod
from typing import Tuple
from exceptions import SMTPAuthError, SMTPServerNotFoundError, SomethingWentWrongError



SERVERS = {
	'gmail.com':('smtp.gmail.com', 465),
	'yahoo.com':('smtp.mail.yahoo.com', 587),
	'outlook.com':('smtp.live.com', 587),
	'icloud.com':('smtp.mail.me.com', 587),
	'office365.com':('smtp.office365.com', 587),
	'aol.com':('smtp.aol.com', 587),
}



def find_server(mail_account: str) -> Tuple[str,int]:
	server = SERVERS.get(mail_account, None)
	return server


def get_host_mail(email) -> str:
	'''
	return the mail server --> example@gmail.com --> gmail.com
	'''

	index_at = email.find('@')
	host = email[index_at + 1:]
	return host



class SMTPServer(ABC):


	@abstractmethod
	def login(self):
		pass



class SMTPServerGmail(SMTPServer):

	def __init__(self, email, password) -> None:
		self.email = email 
		self.password = password


	def login(self) -> Tuple[bool, str]:
		mail_account = get_host_mail(self.email)
		host_port = find_server(mail_account)
	
		host, port = host_port
		is_logged_in = False
		server = None
		try:
			print(self.email , self.password)
			with smtplib.SMTP_SSL(host, port) as server:
				# server.starttls()
				server.login(self.email, self.password)
				is_logged_in = True
				server = server
		except smtplib.SMTPAuthenticationError:
			msg = 'Email or password incorrect ...\nMake sure your account "allows less secure applications"'
			raise SMTPAuthError(msg)

		except:
			raise SomethingWentWrongError()

		return (is_logged_in, server)



class SMTPServerYahoo(SMTPServer):

	def __init__(self, email, password) -> None:
		self.email = email 
		self.password = password


	def login(self) -> Tuple[bool, str]:
		mail_account = get_host_mail(self.email)
		host_port = find_server(mail_account)
		
		host, port = host_port
		is_logged_in = False
		server = None
		try:
			print(self.email , self.password)
			with smtplib.SMTP(host, port) as server:
				server.starttls()
				server.login(self.email, self.password)
				is_logged_in = True
				server = server
		except smtplib.SMTPAuthenticationError:
			msg = 'Email or password incorrect ...\nMake sure your account "allows less secure applications"'
			raise SMTPAuthError(msg)
		except:
			raise SomethingWentWrongError()


		return (is_logged_in, server)



SMTP_CLASSES = {
	'gmail.com':SMTPServerGmail,
	'yahoo.com':SMTPServerYahoo,
	# 'outlook.com':SMTPServerOutlook,
	# 'icloud.com':SMTPServerIcloud,
	# 'office365.com':SMTPServerOffice365,
	# 'aol.com':SMTPServerAol,
}

