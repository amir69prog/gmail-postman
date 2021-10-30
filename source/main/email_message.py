'''
Rendering Mail Message goes here.
we use 'email' package for generating mail message
for more information check following code
'''

from typing import Tuple, Optional, List, BinaryIO, Union

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase

from pathlib import Path


def get_filename(file: str) -> str:
	''' Take the real name with an extention of files and return that for use '''

	try:
		file_extention = file.split('/')[-1] # the file with extention
		finnal_name = file_extention		
	except Exception as err:
		finnal_name = file
	return finnal_name


class GmailMessageRenderer(object):
	''' Rendering the content of an email s'''


	def __init__(self, subject: str, sender: str, reciver: str) -> None:
		
		self.subject = subject
		self.sender = sender
		self.reciver = reciver

		# create and take the multipart message
		self.message = self.make_message() 


	def make_message(self) -> object:
		'''
		Use MIMEMultipart to Create a Message to pass any [Text, Files]
		'''

		message = MIMEMultipart()
		message['Subject'] = self.subject
		message['From'] = self.sender
		message['To'] = self.reciver
		return message


	def attach(self, part: Union[MIMEBase,MIMEText]) -> None:
		''' Attach the part to multipart message '''
		self.message.attach(part)


	def render_text(self, text: str) -> None:
		''' Create MIMEText and attach to message '''
		part = MIMEText(text, 'plain')
		self.attach(part) 


	def render_file(self, file_path: BinaryIO) -> bool:
		''' encoding any file to send mail '''
		
		file_name = get_filename(file_path)
		
		part = MIMEBase('application', 'octet-stream')
		with open(file_path, 'rb') as file:
			part.set_payload(file.read())
		
		encoders.encode_base64(part)
		part.add_header(
		    "Content-Disposition",
		    f"attachment; filename= {Path(file_path).name}",
		)
		self.attach(part)
		return True


	def get_content_message(self) -> str:
		''' the content of message '''
		return self.message.as_string()