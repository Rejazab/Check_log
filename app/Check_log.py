import os
import json
import shlex, subprocess
import re
from datetime import date, datetime, timedelta
from .Error_log_treatment import Error_Log_Processing



class Check_Log:
	__tmp_dir_path = "/tmp/"
	__app_log_path = "/share/logs/*/{app_name}/sub/*{YYMMDD}*"
	__app_server_log_path = "/share/logs/*/{app_name}/server.log"
	__app_jboss_path = "/stand/*/{app_name}"
	__templateCommand_errorLogs = "ssh {serveur_en_cours_de_livraison} \"egrep -ihe 'ERROR|FATAL|EXCEPTION' {path_command}|tail -qn 100\""
	__templateCommand_logs = "ssh {serveur_en_cours_de_livraison} 'tail -qn 15 {path_command}'"
	__data = {}
	__id_release = ""
	__timestamp = ""
	__logs = {}
	__results = {}

	def __init__(self, data, id_release):
		"""
		Init object for the check

		Arguments:
		data -- the kwargs should follow the format app=servers, for exemple: app_1="server_1,server_2,server_3"
		"""
		self.__data = data
		self.__id_release = id_release
		self.__timestamp = datetime.today().strftime("%y%m%d%H%M")
		self.__tmp_dir_path = os.path.dirname(__file__) + self.__tmp_dir_path

	def process_command(self,command_line,server):
		"""
		Execute the command on the server

		Arguments:
		command_line	-- the command to run
		server		-- the server where the command is run

		Return:
		stdout -- return the content from the execution 
		"""
		args = shlex.split(command_line)
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True)
		try:
			stdout,stderr = process.communicate()
			if len(stderr) != 0:
				print ("The following error has append on the server %s: %s \n The command was %s"% (server,stderr,command_line))
			return stdout
		except Exception as err:
			print("Exception occured while executing the command %s on the server %s.\n %s"%(command_line,server,err))

	def init_Log_Check(self, log_date = "700101"):
		"""
		Run the different check.
		"""
		if len(log_date)!=6 or log_date == "700101":
			log_date = date.today().strftime("%y%m%d")

		for app, servers in self.__data.items():
			proper_app = app.replace('_','-')
			for server in servers.split(','):
				self.__get_app_logs(proper_app, server, log_date)
				self.__get_server_logs(proper_app, server)

	def process_log(self, typeLog, logs, app, server, catLog = ""):
		"""
		Process the logs for storage in a JSON file

		Arguments:
		typeLog -- type of the log, should be app or server
		logs 	-- the logs get from the current server
		app 	-- the app which has the logs processed
		server 	-- the server where the logs are processed
		catLog 	-- type of logs to treat, should be empty or error
		"""
		if self.__id_release == '': print("Id release is mandatory.")
		else:
			#Init
			file_path = self.__tmp_dir_path+self.__id_release+'.json'
			try :
				with open(file_path, 'r') as openFile: 
					content = json.load(openFile)
			except Exception as err:
				content = {}
			if app not in content:
				content[app] = {}
			if self.__timestamp not in content[app]:
				content[app][self.__timestamp] = {}
				content[app][self.__timestamp]['app'] = ''
				content[app][self.__timestamp]['server'] = ''
				content[app][self.__timestamp]['app_error'] = ''
				content[app][self.__timestamp]['server_error'] = ''
			
			for timestamp in content[app]:
				first_execution_pid = True if timestamp == self.__timestamp else False
				first_timestamp = timestamp
				break

			#App log
			if typeLog == 'app':
				if catLog == 'error':
					processed_log = re.sub("[0-9]{3}(:[0-9]{2}){3}.[0-9]{3}|\(([a-zA-Z]|[0-9])*\)|\[([0-9]*_([0-9]|[a-zA-Z])*)*\]|[a-zA-Z]* = ([a-zA-Z]|[0-9])*|\[[0-9]*\]|\'([a-zA-Z]|[0-9])*\'|[0-9]*\#+[0-9]*",'',logs)
					log_filter = content[app][self.__timestamp]['app_error'].split('\n') if len(content[app][self.__timestamp]['app_error']) > 0 else []
					final_log = ''
					for log in processed_log.split('\n'):
						if log not in log_filter:
							log_filter.append(log)
							final_log += log+'\n'
					final_log = self.__log_delta(app, final_log, first_execution_pid, content[app][first_timestamp]['app_error'])
					content[app][self.__timestamp]['app_error'] += final_log
				else :
					content[app][self.__timestamp]['app'] += logs

			#Server log
			elif typeLog == 'server':
				if catLog == 'error':
					processed_log = re.sub("[0-9]*(:[0-9]*){2},[0-9]{3}|\'([a-zA-Z]|[0-9])*\'|\'([0-9]*_([0-9]|[a-zA-Z])*)*\'|[0-9]*\#+[0-9]*|task\-[0-9]*",'',logs)
					log_filter = content[app][self.__timestamp]['server_error'].split('\n') if len(content[app][self.__timestamp]['server_error']) > 0 else []
					final_log = ''
					for log in processed_log.split('\n'):
						if log not in log_filter:
							log_filter.append(log)
							final_log += log+'\n'
					final_log = self.__log_delta(app, final_log, first_execution_pid, content[app][first_timestamp]['server_error'])
					content[app][self.__timestamp]['server_error'] += final_log
				else :
					content[app][self.__timestamp]['server'] += logs
			else : 
				print("Type is wrong, should be either app or server")
			with open(file_path, 'w') as outfile:
				json.dump(content, outfile)

	def __get_app_logs(self, app, server, date):
		"""
		Run the logs app command

		Arguments:
		app 	-- the app which has the logs processed
		server 	-- the server where the command is run
		date 	-- logs date with format YYMMDD
		"""
		tmp_log_path = self.__app_log_path.replace('{app_name}',app).replace('{YYMMDD}', date)
		tmp_command = self.__templateCommand_logs.replace('{serveur_en_cours_de_livraison}',server).replace('{path_command}',tmp_log_path)
		self.process_log('app',self.process_command(tmp_command,server),app, server)
		tmp_command = self.__templateCommand_errorLogs.replace('{serveur_en_cours_de_livraison}',server).replace('{path_command}',tmp_log_path)
		self.process_log('app',self.process_command(tmp_command,server),app, server,'error')

	def __get_server_logs(self, app, server):
		"""
		Run the logs server command

		Arguments:
		app 	-- the app which has the logs processed
		server 	-- the server where the command is run
		"""
		tmp_log_path = self.__app_server_log_path.replace('{app_name}',app)
		tmp_command = self.__templateCommand_logs.replace('{serveur_en_cours_de_livraison}',server).replace('{path_command}',tmp_log_path)
		self.process_log('server',self.process_command(tmp_command,server),app, server)
		tmp_command = self.__templateCommand_errorLogs.replace('{serveur_en_cours_de_livraison}',server).replace('{path_command}',tmp_log_path)
		self.process_log('server',self.process_command(tmp_command,server),app, server, 'error')

	def __log_delta(self, app, logs, first_execution_pid, ref_log):
		"""
		Check the logs in error to see if they are true errors or not

		Arguments:
		app 			-- the app which has the logs processed
		logs 			-- the logs to run the check on
		first_execution_pid	-- if it's not the first execution, a check will be made with the first timestamp to know if there are new errors or not after the delivery
		ref_log			-- the error logs from the first execution

		Return:
		filtered_log -- the logs filtered by the exceptions
		"""
		filtered_log = ''
		error_treatment = Error_Log_Processing(app)
		error_treatment.open_exception_file()
		exceptions = error_treatment.get_exception_information()
		if not first_execution_pid :
			for log in logs.split('\n'):
				if log not in exceptions and log not in ref_log:
					filtered_log += log + '\n'
		else:
			for log in logs.split('\n'):
				if log not in exceptions:
					filtered_log += log + '\n'
		error_treatment.update_error_file(filtered_log)
		return filtered_log

	def get_check_results(self):
		"""
		Make a check between the first timestamp and the following ones

		Return a JSON with a status for each kind of log.
		"""
		if self.__id_release == '': print("Id release is mandatory.")
		else:
			#Init
			file_path = self.__tmp_dir_path+self.__id_release+'.json'
			try :
				with open(file_path, 'r') as openFile: 
					content = json.load(openFile)
			except Exception as err:
				self.__results['error'] = 'A check can\'t be made as the file for process id '+self.__id_release+' is empty.'
			for app in content:
				self.__results[app] = {}
				for timestamp in content[app]:
					first_execution_pid = True if timestamp == self.__timestamp else False
					first_timestamp = timestamp
					break
				if not first_execution_pid:
					check_app = 'KO'
					check_server = 'KO'
					check_app_error = 'KO'
					check_server_error = 'KO'

					# Init the list for each log
					current_log_app = content[app][self.__timestamp]['app'].split('\n')
					current_log_server = content[app][self.__timestamp]['server'].split('\n')
					current_log_app_error = content[app][self.__timestamp]['app_error'].split('\n')
					current_log_server_error = content[app][self.__timestamp]['server_error'].split('\n')

					#Check process
					for index_app in reversed(range(len(current_log_app))):
						if current_log_app[index_app] not in content[app][first_timestamp]['app']:
							check_app = 'OK'
							break
					for index_server in reversed(range(len(current_log_server))):
						if current_log_server[index_server] not in content[app][first_timestamp]['server']:
							check_server = 'OK'
							break
					
					check_app_error = 'KO' if len(current_log_app_error) > 1 else 'OK'
					check_server_error = 'KO' if len(current_log_server_error) > 1 else 'OK'

					#Storage of the results
					self.__results[app]['app'] = check_app
					self.__results[app]['server'] = check_server
					self.__results[app]['app_error'] = check_app_error
					self.__results[app]['server_error'] = check_server_error
				else :
					self.__results[app] = "Init successful"
			return self.__results


