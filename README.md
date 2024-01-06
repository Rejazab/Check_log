## Name
Check_Log

## Description
Be able to check the logs and isolate errors which are not really errors.</br>
Allows to know if a delivery add new errors or if the application is still working as intended.</br>

## Usage
How to run the different mains :</br>
py Run_check.py id_release:string log:boolean db:boolean kwargs:app="server,server,..." app="server,server,..." ...</br>
py Run_check.py ef2123FDfgr654 True True app_1="server_1,server_2,server_3" app_2="server_4,server_5,server_6"</br>
py Run_check.py ef2123FDfgr654 True app_1="server_1"</br>
py Run_check.py ef2123FDfgr654 True app_1="server_1,server_2,server_3" app_2="server_2,server_6"</br>

py Update_logs_exceptions.py cleanRepository:boolean args:app_1 app_2 ...'</br>
py Update_logs_exceptions.py True app_1 </br>
py Update_logs_exceptions.py True app_1 app_2</br>
py Update_logs_exceptions.py app_1 app_2 app_3</br>
py Update_logs_exceptions.py app_1  </br>

## License
My own project so, use it if you want.

