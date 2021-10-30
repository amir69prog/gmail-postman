'''
The main app file goes here
set GUI, SMTP, BOX, ETC... 
'''

import sys
import re

from pathlib import Path
from typing import Tuple

from PyQt5.QtWidgets import QWidget, QApplication, QStackedLayout, QFileDialog, QTreeWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.Qt import Qt

from smtp_servers import SMTPGmailServer
from messagebox import MessageBoxError, MessageBoxSuccess
from email_message import GmailMessageRenderer, get_filename

import logging


# get the base dir that is the 'source' directory
BASE_DIR = Path(__file__).resolve().parent.parent # > get "subdir" like (BASE_DIR / 'images')


# set logging Basic Config globaly
logging.basicConfig(
	filename=str(BASE_DIR / 'logging_file.log'),
	format='%(asctime)s %(levelname)s:%(message)s',
	datefmt='%m/%d/%Y-%H:%M:%S'
)



class GreetingLayout(QWidget):
	'''
	the first page that is greeting postman to user
	'''

	def __init__(self, layout: 'QStackedLayout') -> None:
		super().__init__()
		# loading the ui file
		loadUi(BASE_DIR / 'ui/greeting.ui', self)

		self.settings()

		# Attributes 
		self.layout = layout

		# Signals section
		self.start_btn.clicked.connect(self.start)
		self.close_btn.clicked.connect(self.bye_postman)


	def settings(self) -> None:
		''' Set the detail information '''
		self.setWindowTitle('Google Postman')
		self.setFixedSize(810, 529)
		icon_path = BASE_DIR / 'images/Gmail-logo-500x281.png'
		self.setWindowIcon(QIcon(str(icon_path)))



	def start(self):
		self.layout.setCurrentIndex(1)


	def bye_postman(self):
		self.close()


	def keyPressEvent(self, event):
		if event.key() in (Qt.Key_Return, Qt.Key_Enter):
			self.start()
		elif event.key() == Qt.Key_Escape:
			self.bye_postman()


class EmailPasswordLayout(QWidget):
	'''
	Get the email, password from user
	send to 'SendEmailWidget' and check the [account,
	'''

	def __init__(self, layout: 'QStackedLayout', mail_stuff: 'MailStuffLayout') -> None:
		super().__init__()
		# loading the ui file
		loadUi(BASE_DIR / 'ui/postman.ui', self)

		# Attributes
		self.layout = layout
		self.mail_stuff = mail_stuff
		self.avialable_servers = ['gmail.com'] # the avialable smtp servers we use 
		self.default_status = 'Give me your Gmail account...'


		# calling the settings method to set the detail information
		self.settings()


		# Signals Section
		self.next_btn.clicked.connect(self.send_email_and_password)
		self.back_btn.clicked.connect(self.back_to_home)


	def settings(self) -> None:
		''' Set the detail information '''
		self.setWindowTitle('Google Postman')
		self.setFixedSize(810, 529)
		icon_path = BASE_DIR / 'images/Gmail-logo-500x281.png'
		self.setWindowIcon(QIcon(str(icon_path)))


	def validate_email(self,email: str) -> str:
		''' Validate the email '''
		is_valid = True
		message = None

		pattern = re.compile(r"[A-Za-z0-9_]+@[A-Za-z]+\.[A-Za-z]")
		any_match = pattern.search(email)

		if not any_match:
			is_valid = False
			message = 'Invalid email entered.' if not is_valid else None
		
		return message


	def set_status(self, text: str='') -> None:
		self.error.setText(text)


	def set_fields_to_empty(self) -> None:
		'''
		Only for set fields to empty 
		'''
		self.email.setText('')
		self.password.setText('')
		self.set_status(self.default_status)


	def validate_server(self, email: str) -> str:
		''' Ckeck if server email not in avilable servers  '''
		is_valid = True
		message = None
		
		insex_at = email.find('@') + 1
		host_server = email[insex_at:]
		
		if host_server not in self.avialable_servers:
			is_valid = False
			message = 'I\'m working for google post not other services.'
		
		return message


	def validate_fields(self, email: str, password: str) -> Tuple[bool, str]:
		''' validation of email, password '''

		fields = (email, password)
		is_valid = True
		message_if_not_valid = None

		if not all(fields): # ensure the fields must be filled
			is_valid = False
			message_if_not_valid = 'Email and password is required.'
			return (is_valid, message_if_not_valid)

		message_if_not_valid = self.validate_email(email)
		if message_if_not_valid is not None: # this is not valid
			is_valid = False
			return (is_valid, message_if_not_valid)

		message_if_not_valid = self.validate_server(email)
		if message_if_not_valid is not None: # this is not valid
			is_valid = False
			return (is_valid, message_if_not_valid)

		return (is_valid, message_if_not_valid)


	def send_email_and_password(self) -> None:
		''' Get and validate the data process goes here  '''
		email = self.email.text()
		password = self.password.text()
		is_valid, message_if_not_valid = self.validate_fields(email, password)
		if is_valid:
			server = SMTPGmailServer(email, password)

			title, message_if_has_error = server.login()

			if message_if_has_error:
				logging.error(message_if_has_error)
				self.set_status('Error occurred...')
				message_box_error = MessageBoxError(self, title, message_if_has_error)
				message_box_error.exec_()
			else:
				self.set_fields_to_empty()
				self.mail_stuff.email = email
				self.mail_stuff.password = password
				self.mail_stuff.server = server

				self.go_to_email_stuff()

		else:
			self.set_status(message_if_not_valid)


	def go_to_email_stuff(self):
		self.layout.setCurrentIndex(2)


	def back_to_home(self):
		self.layout.setCurrentIndex(0)


	def keyPressEvent(self, event):
		if event.key() in (Qt.Key_Return, Qt.Key_Enter):
			self.send_email_and_password()
		elif event.key() == Qt.Key_Escape:
			self.back_to_home()


class MailStuffLayout(QWidget):
	'''
	bring the mail to postman who send our mail :)
	'''

	def __init__(self, layout, server=None ,email=None, password=None):
		super().__init__()
		loadUi(BASE_DIR / 'ui/postman_stuff.ui', self)

		# Attributes
		self.layout = layout
		self.email = email
		self.password = password
		self.server = server
		self.path_files = []
		self.default_status = 'Ok now pass your mail information'
		self.filter_files = 'All Files (*.*)'



		# calling the settings method to set the detail information
		self.settings()


		# Signals section
		self.send_btn.clicked.connect(self.send_mail)
		self.back_btn.clicked.connect(self.back_to_email_pasword)
		self.insert_file_btn.clicked.connect(self.insert_files)
		self.files_tree.activated.connect(self.remove_file)


	def settings(self):
		''' Set the detail information '''
		self.setWindowTitle('Google Postman')
		self.setFixedSize(810, 529)
		icon_path = BASE_DIR / 'images/Gmail-logo-500x281.png'
		self.setWindowIcon(QIcon(str(icon_path)))


	def set_status(self, text: str='') -> None:
		self.error.setText(text)


	def validate_email(self,email: str) -> str:
		''' Validate the email '''
		is_valid = True
		message = None

		pattern = re.compile(r"[A-Za-z0-9_]+@[A-Za-z]+\.[A-Za-z]")
		any_match = pattern.search(email)

		if not any_match:
			is_valid = False
			message = 'Invalid Reciever Inserted.'
		
		return message


	def validate_require_fields(self, reciver, text, files):
		is_valid = True
		message = None
		require_files = (text, files)

		if reciver in [None, '']:
			is_valid = False
			message = 'Reciever is required.'
		elif not any(require_files):
			is_valid = False
			message = 'Content or Files is required.'

		return message


	def send_mail(self):
		subject = self.subject.text()
		reciver = self.reciever.text()
		text = self.message.toPlainText()
		
		if text.isspace(): # if that just space! not correct ok!!
			text = '' # set it to null to validate

		message_if_not_valid = self.validate_require_fields(reciver, text, self.path_files)
		if message_if_not_valid is not None:
			self.set_status(message_if_not_valid)
			return

		message_if_not_valid = self.validate_email(reciver)
		if message_if_not_valid is not None:
			self.set_status(message_if_not_valid)
			return

		
		message = GmailMessageRenderer(subject,self.email, reciver)
		message.render_text(text)
		if self.path_files:
			for file in self.path_files:
				# self.loading_git = QMovie(str(BASE_DIR / 'images/loading.gif'))
				# self.loading.setMovie(self.loading_git)
				# self.start_loading()
				status = message.render_file(file)
				# if status:
				# 	self.stop_and_close_loading()

		content = message.get_content_message()

		title, message_if_has_error = self.server.send_mail(
			reciver,
			content
		)
		
		if message_if_has_error is not None:
			logging.error(message_if_has_error)
			self.set_status('Error occurred...')
			message_box_error = MessageBoxError(self, title, message_if_has_error)
			message_box_error.exec_()
		else:
			self.set_fields_to_empty()
			msg = MessageBoxSuccess(self, "Your email has being sent successfully.")
			msg.exec_()


	def insert_files(self):
		file_dialog = QFileDialog()
		path_files = file_dialog.getOpenFileNames(self, 'Insert Files',str(BASE_DIR),filter=self.filter_files)
		for index, file in enumerate(path_files[0]):
			if file not in self.path_files:
				self.path_files.append(file)
				self.files_tree.addItem(get_filename(file),userData=file)
				self.files_tree.adjustSize()


	def remove_file(self,index):
		try:
			raise ValueError('not found the item in list')
			file_name = self.files_tree.itemData(index)
			self.files_tree.removeItem(index)
			self.path_files.remove(file_name)
			self.files_tree.adjustSize()
		except ValueError as err:
			logging.error(str(err))


	def set_fields_to_empty(self):
		self.set_status(self.default_status)
		self.subject.setText('')
		self.reciever.setText('')
		self.message.clear()
		self.path_files = []
		self.files_tree.clear()



	def back_to_email_pasword(self):
		self.set_status(self.default_status)
		self.layout.setCurrentIndex(1)


	def start_loading(self):
		self.loading_git.start()


	def stop_and_close_loading(self):
		self.loading_git.stop()
		self.loading.hide()


	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.back_to_email_pasword()



if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	layout = QStackedLayout()
	
	greeting = GreetingLayout(layout)
	mail_stuff = MailStuffLayout(layout)
	email_password = EmailPasswordLayout(layout, mail_stuff)

	layout.insertWidget(0, greeting)
	layout.insertWidget(1, email_password)
	layout.insertWidget(2, mail_stuff)
	
	app.exec_()

