'''
the important process goes here
we use SMTP to send/login to Gmail account  
only for gmail smtp server
'''


import smtplib
from abc import ABC, abstractmethod
from typing import Tuple, Union

# aliases
Email = str
Content = str
Password = str
Title = str


class SMTPServer(ABC):

	@abstractmethod
	def login(self):
		pass
	

	@abstractmethod
	def send_mail(self):
		pass


class SMTPGmailServer(SMTPServer):
	''' logging and sending mail to the Gmail SMTP Server '''


	def __init__(self, email: Email, password: Password):

		self.host_and_port = ('smtp.gmail.com', 465)
		self.email = email
		self.password = password
		self.server = None
		self.messages = self.generate_message()
		self.error_message = None


	def generate_message(self) -> dict:
		''' Publish possible error messages '''

		messages = {
			'SMTPAuthenticationError':'Most probably the server didn’t accept the username/password combination provided. Make sure your account Allow "Less secure app access"',
			'SMTPNotSupportedError':'The command or option attempted is not supported by the server.',
			'SMTPConnectError':'Error occurred during establishment of a connection with the server.',
			'SMTPDataError':'The SMTP server refused to accept the message data.',
			'SMTPServerDisconnected':'server unexpectedly disconnected.',
			'gaierror':'Please check your network.',
		}
		return messages


	def login(self) -> Tuple[Union[Title, None], Union[Content, None]]:
		'''
		logging the available accounts to the smtp server
			note: cannot login to smtp server of unavialable accounts

		'''

		try:
			with smtplib.SMTP_SSL(*self.host_and_port) as server:
				server.login(self.email, self.password)
				# Done...
				self.server = server
			
		except Exception as error:
			title = error.__class__.__name__
			self.error_message = self.messages.get(title,'Something went wrong!')
			return (title, self.error_message)
		else:
			return (None, None)


	def send_mail(self, reciver: Email, content: Content) -> Tuple[Union[Title, None], Union[Content, None]]:
		'''
		Sending email to account. also again logging to account and i think this is a bad way to do
		'''

		try:
			with smtplib.SMTP_SSL(*self.host_and_port) as server:
				server.login(self.email, self.password) # i hate this code but i dont what to do...
				server.sendmail(self.email, reciver, content)
		except Exception as error:
			title = error.__class__.__name__
			self.error_message = self.messages.get(title,'Something went wrong!')
			return (title, self.error_message)
		else:
			return (None, None)
