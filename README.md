## Name
Check_Log

## Description
Be able to check the logs and isolate errors which are not really errors.
Allow to know if a delivery add new errors or if the application is still working as intended.

## Usage
How to run the different mains :
py Run_check.py id_release:string log:boolean db:boolean kwargs:app="server,server,..." app="server,server,..." ...
py Run_check.py ef2123FDfgr654 True True app_1="server_1,server_2,server_3" app_2="server_4,server_5,server_6"
py Run_check.py ef2123FDfgr654 True app_1="server_1"
py Run_check.py ef2123FDfgr654 True app_1="server_1,server_2,server_3" app_2="server_2,server_6"

py Update_logs_exceptions.py cleanRepository:boolean args:app_1 app_2 ...'
py Update_logs_exceptions.py True app_1 
py Update_logs_exceptions.py True app_1 app_2
py Update_logs_exceptions.py app_1 app_2 app_3
py Update_logs_exceptions.py app_1  

## License
My own project so, use it if you want.

