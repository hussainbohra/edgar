import pymysql.cursors
from utils import FileHelper

class RDSProcessor:
    def __init__(self, config_file):
        self.rds_info = self.parse_config(config_file) 
    
    def parse_config(self, config_file):
        creds = {}
        content = FileHelper.get_content(config_file)
        for line in content.split('\n'):
            data = line.split('=')
            if len(data[0]) > 0:
                creds[data[0]] = data[1]
        return creds
    
    def get_connection(self):
        conn = pymysql.connect(host=self.rds_info['host'],
                             user=self.rds_info['user'],
                             password=self.rds_info['password'],
                             db=self.rds_info['db'],
                             port=int(self.rds_info['port']),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        return conn
    
    def get_query(self, sql_query):
        result = None
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchall()
        finally:
            conn.close()            
        return result
    