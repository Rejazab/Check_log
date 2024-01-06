import os
import sys
from app.Error_log_treatment import Error_Log_Processing

class Update_logs_exceptions:
	__list_app = []
	__tmp_dir_path = 'app/tmp'

	def __init__(self, args, cleanRepository = 'False'):
		"""
		Init the run of the update for the exception files

		Arguments:
		args 			-- name of the app file to make the update on
		cleanRepository -- run the cleaning of the tmp repository
		"""
		self.__list_app = args
		self.__tmp_dir_path = os.path.realpath(__file__).replace(__file__,'') + self.__tmp_dir_path
		self.run_Update()
		if cleanRepository == 'True':
			self.__clean_repository()

	def run_Update(self):
		"""
		Run the update of the files from error to exception

		Return:
		results -- the results of the update for each app
		"""
		results = {}
		for app in self.__list_app:
			app_error_to_update = Error_Log_Processing(app.replace('_','-'))
			results[app] = app_error_to_update.add_error()
		print(results)

	def __clean_repository(self):
		"""
		Remove the files in the tmp repository
		"""
		results = {}
		for file in os.listdir(self.__tmp_dir_path):
			try:
				os.remove(self.__tmp_dir_path +'/'+ file)
				results[file] = 'Successfully remove.'
			except Exception as err:
				results[file] = 'The following error was met : '+str(err)
		print(results)



def main(cleanRepository = False, *args):
	"""
	Main use to call the class 'Update_logs_exceptions' directly with args from the cmd
	"""
	Update_logs_exceptions(args, cleanRepository)

if __name__ == "__main__":
	if sys.argv[1] in ("True","False") and len(sys.argv) == 1:
		main(sys.argv[1])
	elif sys.argv[1] not in ("True","False"):
		main(False,
			*sys.argv[1:]
			)
	elif sys.argv[2] not in ("True","False"):
		main(sys.argv[1],
			*sys.argv[2:]
			)
	else:
		print('The format is :\npy Update_logs_exceptions.py cleanRepository:boolean *args:app_1 app_2 ...')
