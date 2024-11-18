import pymysql

def connect_to_mysql():
    # Connect to MySQL database
    connection = pymysql.connect(
        host='icohold.anamai.moph.go.th', # database server
        port=3306,
        database='aidoc_development',	
        user='patiwet', 	# mysql username
        password='icoh2017p@ssw0rd' 	# mysql password for the username
    )
    return connection
    

if __name__ == "__main__":
    connect_to_mysql()

