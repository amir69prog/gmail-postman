'''
The Box like Error and Succes message
'''

from PyQt5.QtWidgets import QMessageBox



class MessageBoxError(QMessageBox):

	def __init__(self, parent: object, title: str, error_message: str) -> None:
		super().__init__(parent)
		self.setWindowTitle(title)

		self.setStyleSheet('''
			QLabel {
				color:#000;
				font: 14pt "Yagut";
			}
		''')
		self.setText(error_message)
		self.setIcon(QMessageBox.Critical)


		self.show()


class MessageBoxSuccess(QMessageBox):

	def __init__(self, parent: object, text: str) -> None:
		super().__init__(parent)
		self.setWindowTitle('Google Postman')

		self.setStyleSheet('''
			QLabel {
				color:#000;
				font: 14pt "Yagut";
			}
		''')
		self.setText(text)
		self.setIcon(QMessageBox.Information)


		self.show()