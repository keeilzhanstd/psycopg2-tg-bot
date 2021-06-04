import psycopg2
import config
from pprint import pprint

def executor(method):
	def wrapper(*args, **kwargs):
		args[0].cursor = args[0].connection.cursor()
		rec = method(*args, **kwargs)
		args[0].cursor.close()
		return rec
	return wrapper

class DBConnection:
	def __init__(self):
		try:
			self.connection = psycopg2.connect(dbname=config.DBNAME, user=config.USER, password=config.PASSWORD, port=config.PORT)
			self.connection.autocommit = True
			self.create_table()
		except:
			pprint("Cannot connect to database")

	@executor
	def create_table(self):
		try:
			create_table_command = "CREATE TABLE IF NOT EXISTS users(id serial PRIMARY KEY, username VARCHAR (50) UNIQUE, name varchar(100), surname varchar(100), age integer NOT NULL)"
			self.cursor.execute(create_table_command)
		except:
			pprint("table creation failed or table already exists")

	@executor
	def insert_record(self, username, name, surname, age):
		new_record = (username, name, surname, age)
		insert_command = "INSERT INTO users(username, name, surname, age) VALUES('" + new_record[0] + "','" + new_record[1] + "','" + new_record[2] + "','" + new_record[3] + "')"
		pprint(insert_command)
		self.cursor.execute(insert_command)

	@executor
	def find_record(self, username):
		search_record = (username)
		search_command = "SELECT * FROM users WHERE username = '" + search_record + "'"
		self.cursor.execute(search_command)
		found_record = self.cursor.fetchall()
		return found_record

	@executor
	def delete_record(self, username):
		delete_record = (username)
		delete_command = "DELETE FROM users WHERE username = '" + delete_record + "'"
		self.cursor.execute(delete_command)

	@executor
	def update_record(self, username, name, surname, age):
		update_record = (username, name, surname, age)
		update_command = "UPDATE users SET name = '" + update_record[1] + "', surname = '" + update_record[2] + "', age = '" + update_record[3] + "' WHERE username = '" + update_record[0] + "'"
		self.cursor.execute(update_command)

	@executor
	def query_all(self):
		query_command = "SELECT * FROM users"
		self.cursor.execute(query_command)
		users = self.cursor.fetchall()
		return users

if __name__=='__main__':
	db = DBConnection()
	#db.insert_record("turgunbaev", "beks", "turgun", "28")
	#x = db.find_record("oncekeeilzhan")
	#print(x)
	#x = db.query_all()
	#print(x)
	#db.update_record("turgunbaev", "beksultan", "turgunbaev", "21")
	#db.delete_record("oncekeeilzhan")