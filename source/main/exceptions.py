
class SMTPServerNotFoundError(ValueError):
	def __init__(self, msg=None):
		super().__init__(msg)


class SMTPAuthError(ValueError):
	def __init__(self, msg):
		super().__init__(msg)


class SomethingWentWrongError(ValueError):
	def __init__(self):
		super().__init__()