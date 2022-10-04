"""
This script takes a json file whit ADS data filtered and put into a local DB (mariaDB)
"""

import json
import pymysql



# Create a connection object
Host = "localhost"  
User = "user"       
Password = ""           
database = "database_name"