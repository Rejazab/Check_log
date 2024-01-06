import sys
from app.Check_log import Check_Log
from app.Check_DB_transaction import Check_DB_Transaction

class Run_Check:
	__checkDB = False
	__checkLog = False
	__id_release = ''
	__data = {}

	def __init__(self, id_release, kwargs, checkLog = False, checkDB = False):
		"""
		Init object for the check

		Arguments:
		kwargs 	 -- the kwargs should follow the format app=servers, for exemple: app_1="server_1,server_2,server_3"
		checkDB  -- boolean to know if we have to run the check DB
		checkLog -- boolean to know if we have to run the check on the log
		"""
		self.__checkDB = checkDB
		self.__checkLog = checkLog
		self.__data = kwargs
		self.__id_release = id_release
		self.execute()

	def execute(self):
		"""
		Execute the different check and return the results

		Return:
		results	-- all the information from the checks in a JSON format
		"""
		results = {}
		if self.__checkLog == 'True':
			results["log"] = self.__run_LOG_checked()
		if self.__checkDB == 'True':
			results["db"]  = self.__run_DB_checked()
		print(results)

	def __run_DB_checked(self):
		"""
		Run the check on the DB logs

		Return:
		json -- contains the result of the check on the DB for each server
		"""
		Check_DB = Check_DB_Transaction(self.__data)
		Check_DB.init_DB_check()
		return Check_DB.get_logs_from_convention(True)
		

	def __run_LOG_checked(self):
		"""
		Run the check on the app and server logs

		Return:
		json -- contains the results of the check on the logs for each app
		"""
		Check_LOG = Check_Log(self.__data, self.__id_release)
		Check_LOG.init_Log_Check()
		return Check_LOG.get_check_results()


def main(id_release, log = False, db = False, **kwargs):
	"""
	Main use to call the class 'Run_Check' directly with args from the cmd
	"""
	Run_Check(id_release, kwargs, log, db)

if __name__ == "__main__":
	if sys.argv[1] in ("True","False"):
		print('The format is :\npy Run_check.py id_release:string log:boolean db:boolean **kwargs:app_1="server_1,server_2,..." app_2="server_2,server_4,..." ...')
	elif sys.argv[2] not in ("True","False"):
		main(sys.argv[1],
			**dict(arg.split("=") for arg in sys.argv[2:]))
	elif sys.argv[3] not in ("True","False"):
		main(sys.argv[1],
			sys.argv[2],
			**dict(arg.split("=") for arg in sys.argv[3:])
			)
	elif sys.argv[4] not in ("True","False"):
		main(sys.argv[1],
			sys.argv[2],
			sys.argv[3],
			**dict(arg.split("=") for arg in sys.argv[4:])
			)
	else:
		print('The format is :\npy Run_check.py id_release:string log:boolean db:boolean **kwargs:app_1="server_1,server_2,..." app_2="server_1,server_3,..." ...')


