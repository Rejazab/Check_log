import os
import json
import shlex, subprocess
from datetime import date, datetime, timedelta
import time

class Check_DB_Transaction:
	

	__configFile = '/conf/referentiel.txt'
	__templateCommandconv = "ssh admin@{serveur_en_cours_de_livraison} 'grep -h conv.*otb {chemin_log_application}/server/info*.log.{YYMMDD}  | tail -5'"
	__templateCommandDB = "ssh admin@const_server '/realpath/private_script.sh -a {arg1} -b {arg2} -d {YYYYMMDD}' 2>/dev/null"
	__data = {}
	__organizedData = {}
	__returnData = {}

	def __init__(self, data):
		"""
		Init object for the check

		Arguments:
		data -- the kwargs should follow the format app=servers, for exemple: app_1="server_1,server_2,server_3"
		"""
		self.__data = data
		self.__configFile = os.path.dirname(__file__) + self.__configFile

	def init_DB_check(self):
		""" 
		Initialize the different variables which will be used then run the different checks
		"""
		# Prepare the referentiel and variables
		for webapp, servers in self.__data.items():
			proper_webapp = webapp.replace("_","-")
			if proper_webapp not in self.__organizedData: self.__organizedData[proper_webapp] = {}
			if 'servers' not in self.__organizedData[proper_webapp]: self.__organizedData[proper_webapp]['servers'] = []
			if 'path' not in self.__organizedData[proper_webapp]: self.__organizedData[proper_webapp]['path'] = []
			if 'db_command' not in self.__organizedData[proper_webapp]: self.__organizedData[proper_webapp]['db_command'] = {}
			if 'check_DB' not in self.__organizedData[proper_webapp]: self.__organizedData[proper_webapp]['check_DB'] = {}
			for server in servers.split(","):
				if server not in self.__organizedData[proper_webapp]['servers']: self.__organizedData[proper_webapp]['servers'].append(server)

			self.__get_information_from_referentiel(webapp.replace("_","-"))

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

	def __get_information_from_referentiel(self,webapp):
		"""
		Read the configuration file and look for match with the webapp to get the path where the logs will be read.

		Arguments:
		self	-- object to use for the variable
		webapp 	-- the webapp to find the path for, must be String
		"""
		file = open(self.__configFile)
		dataRef = json.load(file)
		for key in dataRef:
			if webapp in dataRef[key]["modules"]:
				self.__organizedData[webapp]["path"] = dataRef[key]['path']

	def __treatment_log_conv(self,output, log_date):
		"""
		Extract the data from the conv.
		The data are returned through a dictionnary to be stored on __organizedData

		Arguments:
		output	 -- the data from log conv
		log_date -- date of the logs to check, format will be changed from YYMMDD to YYYYMMDD
		
		Return:
		db_command -- list of command to pass for the check on the DB
		"""
		db_command = []
		output_row = output.split("\n")
		for row in output_row:
			tmp = row.split(";")
			if(len(tmp) > 1):
				tmp_command = self.__templateCommandDB.replace("{arg1}",tmp[2].split("/")[3])
				tmp_command = tmp_command.replace("{arg2}", tmp[9])
				tmp_command = tmp_command.replace("{YYYYMMDD}", datetime.strptime(log_date, "%y%m%d").strftime("%Y%m%d"))
				db_command.append(tmp_command)
		return db_command

	def __get_informations_from_DB(self):
		"""
		Get the informations from the DB using the data from the conv logs
		"""
		indexes = lambda data_list, element: [index for index,string in enumerate(data_list) if element in string]
		for webapp in self.__organizedData:
			self.__returnData['check_DB'][webapp] = {}
			for server in self.__organizedData[webapp]['db_command']:
				for command_line in self.__organizedData[webapp]['db_command'][server]:
					#print("command %s"% command_line)
					if len(command_line) > 1:
						try:
							raw_data = self.process_command(command_line,server)
							data = raw_data.split("\n")
							current_date = (datetime.now()-timedelta(minutes=10)).strftime("%d-%b-%y %H.%M.%S.%f")
							creation_date = datetime.strptime(data[indexes(data,'CREATION_DATE')[0]].split('=')[1].replace('  ',''),' %d-%b-%y %I.%M.%S.%f %p').strftime("%d-%b-%y %H.%M.%S.%f")
							status = data[indexes(data,'STATUS')[0]].split("=")[1].replace(' ','')
							creation_date = creation_date if creation_date > current_date else 'before delivery'
							if creation_date != 'before delivery' and 'catch' in status:
								self.__organizedData[webapp]['check_DB'][server] = "OK"
								self.__returnData['check_DB'][webapp][server] = "OK"
								break
							self.__organizedData[webapp]['check_DB'][server] = "KO"
							self.__returnData['check_DB'][webapp][server] =  "KO"
						except Exception as err:
							self.__organizedData[webapp]['check_DB'][server] = "KO"
							self.__returnData['check_DB'][webapp][server] = "KO"

	def get_logs_from_conv(self, toTreat = False, log_date = "700101"):
		"""
		Run shell command to get the log from files and store it in the dict __organizedData

		Arguments:
		toTreat	 -- boolean to know if we have to run the treatment for the DB check, false by default
		log_date -- date of the logs to check, default value is current date and format should be YYMMDD

		Return:
		self.__returnData['check_DB'] -- a dictionnary allowing to know if data where insert in the DB or not
		"""
		if len(log_date)!=6 or log_date == "700101":
			log_date = date.today().strftime("%y%m%d")

		for webapp in self.__organizedData:
			info_webapp = self.__organizedData[webapp]
			tmp_commandeconv = self.__templateCommandconv.replace('{YYMMDD}',log_date).replace('{chemin_log_application}',info_webapp['path'])
			for server in info_webapp['servers']:
				command_line = tmp_commandeconv.replace('{serveur_en_cours_de_livraison}',server)
				self.__organizedData[webapp]['db_command'][server] = self.__treatment_log_conv(self.process_command(command_line,server),log_date)
		if toTreat :
			self.__returnData['check_DB'] = {}
			self.__get_informations_from_DB()
			return self.__returnData['check_DB']
