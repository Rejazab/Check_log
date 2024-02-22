import os
import json
from datetime import date, datetime, timedelta

class ErrorLogProcessing:
	__error_file = "/data/errors_{app}.txt"
	__exception_file = "/data/exceptions_{app}.txt" 
	__exceptions = ''

	def __init__(self, app):
		"""
		Init object for the errors treatment

		Arguments:
		app -- the app where the logs are processed
		"""
		self.__error_file = os.path.dirname(__file__) + self.__error_file.replace('{app}',app)
		self.__exception_file = os.path.dirname(__file__) + self.__exception_file.replace('{app}',app)

	def open_exception_file(self):
		"""
		Read the exceptions for the current application and saved it in a private var
		"""
		try :
			with open(self.__exception_file, 'r') as openFile: 
				self.__exceptions = openFile.read()
		except Exception as err:
			with open(self.__exception_file, 'x') as newFile:
				newFile.write('')

	def update_error_file(self, logs):
		"""
		Update the content of the app error file with the last error get from the server and app

		Arguments:
		logs -- the logs to add in the file
		"""
		try :
			with open(self.__error_file, 'r') as openFile: 
				content = openFile.read() + logs
		except Exception as err:
			content = logs
		with open(self.__error_file, 'w') as outfile:
			outfile.write(content)

	def get_exception_information(self):
		"""
		Return the content of the exception file
		"""
		return self.__exceptions

	def add_error(self):
		"""
		Update the exception file with the new errors found and remove the error file

		Return the results of the processing
		"""
		content_errors = ''
		content_exceptions = ''
		results = ''
		number_of_row = 0

		try :
			with open(self.__error_file, 'r') as errorFile:
				content_errors = errorFile.read()
				try:
					with open(self.__exception_file, 'r') as exceptionFile: 
						content_exceptions = exceptionFile.read()
					for row in content_errors.split('\n'):
						if row not in content_exceptions:
							content_exceptions += row + '\n'
							number_of_row += 1
					with open(self.__exception_file, 'w') as exceptionFile: 
						exceptionFile.write(content_exceptions)
						results += 'New rows added to the exceptions : '+str(number_of_row)
						os.remove(self.__error_file)
				except Exception as err :
					results += 'File exception '+self.__exception_file+' with the error : '+str(err)
		except Exception as err:
			results += 'File error '+self.__error_file+' with the error : '+str(err)
		return results