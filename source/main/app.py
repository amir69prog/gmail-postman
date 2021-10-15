import sys
import os
import re
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QWidget, QStackedLayout
from PyQt5 import QtCore,QtGui
from pathlib import Path

from smtp_servers import SMTP_CLASSES, get_host_mail
import exceptions


''' 
todo:
	--> Download all image of smtp servers


'''


path = Path(__file__).parent.parent


class EmailStuffWidget(QWidget):
	''' The Email Stuff : Send email , Retrieve emails and more '''

	def __init__(self, layout, smtp_server=None):
		super().__init__()
		loadUi(path / 'ui/email_stuff.ui', self)

		self.layout = layout
		self.smtp_server = smtp_server

		# Signals
		self.back_btn.clicked.connect(self.back_to_home)

	def back_to_home(self):
		self.layout.setCurrentIndex(0)


class MainApp(QWidget):
	''' The Main Widget : login to mail account '''

	def __init__(self, layout, email_stuff):
		super().__init__()
		loadUi(path / 'ui/login_page.ui',self)
		
		self.layout = layout
		self.email_stuff = email_stuff

		self.close_btn.clicked.connect(self.close_)
		self.login_btn.clicked.connect(self.login)

		self.settings()


	def settings(self):
		self.setFixedSize(649, 517)


	def close_(self) -> None:
		self.close()


	def set_empty_fields(self):
		self.set_error()
		self.email.setText('')
		self.password.setText('')

	def set_error(self, text: str ='') -> None:
		self.error.setText(text)


	def validate_regex(self,email):
		pattern = re.compile(r"[A-Za-z0-9_]+@[A-Za-z]+\.com")
		validate = pattern.findall(email)
		is_valid = True if validate else False
		return is_valid


	def validate_mail(self, email, password) -> None:
		# todo: refactor this method
		is_valid = True
		if not all([email, password]):
			self.set_error('* Email and password is required.')
			is_valid = False
			return is_valid


		valid_regex = self.validate_regex(email)
		if not valid_regex:
			self.set_error('Invalid Email passed.')
			is_valid = False
			return is_valid

		return is_valid
		

	def login(self):
		# get the username , password and redirect to send email
		email = self.email.text()
		password = self.password.text()
		is_valid = self.validate_mail(email, password)
		if is_valid:
			try:
				mail_server = get_host_mail(email)
				mail_account = SMTP_CLASSES.get(mail_server,None)

				if not mail_account:
					msg = 'i could not found the smtp server'
					raise exceptions.SMTPServerNotFoundError(msg)
				
				account = mail_account(email, password)
				status, server = account.login()
				self.set_error('Successfully Logged in.')
				if status:
					# redirect to send email page
					self.email_stuff.server = server
					self.layout.setCurrentIndex(1)
					self.set_empty_fields()


			except exceptions.SMTPAuthError as err:
				self.set_error(str(err))

			except exceptions.SMTPServerNotFoundError as err:
				self.set_error(str(err))
				# todo : create a widget to show what smtp servers we support 

			except exceptions.SomethingWentWrongError as err:
				self.set_error(str(err))

				# information widget


if __name__ == '__main__':
	app = QApplication(sys.argv)
	layout = QStackedLayout()
	
	email_stuff = EmailStuffWidget(layout)
	main = MainApp(layout,email_stuff)

	layout.insertWidget(0, main)
	layout.insertWidget(1, email_stuff)

	app.exec_()