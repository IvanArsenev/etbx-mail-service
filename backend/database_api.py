import sqlite3
con = sqlite3.connect("database.db")

def db_request(request):
	cursor = con.cursor()
	cursor.execute(request)
	con.commit()
	return cursor

def login_user(login, password):
	cursor = db_request(f'SELECT * FROM users WHERE mail = "{login}" AND password = "{password}"')
	userId = cursor.fetchall()
	if userId:
		return True
	return False

def get_user(login):
	cursor = db_request(f'SELECT * FROM users WHERE mail = "{login}"')
	userId = cursor.fetchall()
	if userId:
		return [True, userId]
	return [False]

def unauthorised_token(token):
	cursor = db_request(f'SELECT * FROM disabled_tokens WHERE token = "{token}"')
	userId = cursor.fetchall()
	if userId:
		return True
	return False

def get_messages_sended_db(login):
	cursor = db_request(f'SELECT * FROM mails WHERE sender = "{login}"')
	messages_db = cursor.fetchall()
	messages_array = []
	for message in messages_db:
		messages_array.append(message)
	return messages_array

def get_messages_recieved_db(login):
	cursor = db_request(f'SELECT * FROM mails WHERE reciever = "{login}"')
	messages_db = cursor.fetchall()
	messages_array = []
	for message in messages_db:
		messages_array.append(message)
	return messages_array