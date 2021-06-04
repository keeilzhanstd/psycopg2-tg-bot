import config
import telebot
import database
from telebot import types

bot = telebot.TeleBot(config.TOKEN_API)
db = database.DBConnection()

def validate_string(string):
	return string.isalpha()

def validate_digits(string):
	return string.isdigit()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):

	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	c_button = types.KeyboardButton('/register')
	d_button = types.KeyboardButton('/delete')
	u_button = types.KeyboardButton('/update')
	v_button = types.KeyboardButton('/me')
	a_button = types.KeyboardButton('/users')
	markup.add(c_button, d_button, v_button, u_button, a_button)

	bot.reply_to(message, f'Я зарегистрирую тебя в базу данных.\nНадеюсь на твою помощь, {message.from_user.first_name} {message.from_user.last_name}!', reply_markup=markup)


savedata = {}

@bot.message_handler(commands=['register'])
def askname(message):
	markup = types.ReplyKeyboardRemove(selective=False)
	msg = bot.send_message(message.chat.id, "Ваше имя?", reply_markup=markup)
	savedata["username"] = message.from_user.username
	bot.register_next_step_handler(msg, process_name)

def process_name(message):
	try:
		if validate_string(message.text):
			savedata["name"] = message.text
			msg = bot.send_message(message.chat.id, "Ваша фамилия?")
			bot.register_next_step_handler(msg, process_last_name)
		else:
			msg = bot.send_message(message.chat.id, "Введите имя. Оно должно содержать только буквы, и никаких знаков и цифр.")
			bot.register_next_step_handler(msg, process_name)
	except Exception as e:
		bot.reply_to(message, e)

def process_last_name(message):
	try:
		if validate_string(message.text):
			savedata["last_name"] = message.text
			msg = bot.send_message(message.chat.id, "Ваш возраст?")
			bot.register_next_step_handler(msg, process_age)
		else:
			msg = bot.send_message(message.chat.id, "Введите фамилию. Она должна содержать только буквы, и никаких знаков и цифр.")
			bot.register_next_step_handler(msg, process_last_name)
	except Exception as e:
		bot.reply_to(message, e)


def process_age(message):
	try:
		if validate_digits(message.text):
			savedata["age"] = message.text
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
			y_button = types.KeyboardButton('Да')
			n_button = types.KeyboardButton('Нет')
			markup.add(y_button, n_button)
			msg = bot.send_message(message.chat.id, f'Ваша анкета: \nИмя: {savedata["name"]} \nФамилия: {savedata["last_name"]} \nВозраст: {savedata["age"]}\nЗарегистрироваться?', reply_markup=markup)
			bot.register_next_step_handler(msg, process_register)
		else:
			msg = bot.send_message(message.chat.id, "Введите возраст. Он должен содержать лишь цифры.")
			bot.register_next_step_handler(msg, process_age)
	except Exception as e:
		bot.reply_to(message, e)


def process_register(message):
	if message.text == "Да":
		username = savedata["username"]
		name = savedata["name"]
		surname = savedata["last_name"]
		age = savedata["age"]

		try:
			db.insert_record(username, name, surname, age)
			markup = types.ReplyKeyboardRemove(selective=False)
			msg = bot.send_message(message.chat.id, "Вы успешно зарегестрированы.", reply_markup=markup)
		except Exception as e:
			print(e)
			markup = types.ReplyKeyboardRemove(selective=False)
			msg = bot.send_message(message.chat.id, "Вы уже зарегестрированы в нашей базе данных.", reply_markup=markup)
	elif message.text == "Нет":
		markup = types.ReplyKeyboardRemove(selective=False)
		msg = bot.send_message(message.chat.id, "Отмена регистации анкеты.", reply_markup=markup)
		
@bot.message_handler(commands=['delete'])
def delete_own_record_prompt(message):
	record = db.find_record(message.from_user.username)
	userdata = {}
	if len(record) != 0:
		found = record[0]
		userdata["name"] = found[2]
		userdata["last_name"] = found[3]
		userdata["age"] = found[4]
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
		y_button = types.KeyboardButton('Да')
		n_button = types.KeyboardButton('Нет')
		markup.add(y_button, n_button)
		msg = bot.send_message(message.chat.id, f'Ваша предыдущая анкета:\nИмя: {userdata["name"]}\nФамилия: {userdata["last_name"]}\nВозраст: {userdata["age"]}\nУдалить?', reply_markup=markup)
		bot.register_next_step_handler(msg, delete_own_record)
	else:
		msg = bot.send_message(message.chat.id, "Вашей анкеты еще нету в базе данных!")

def delete_own_record(message):
	if message.text == "Да":
		try:
			db.delete_record(message.from_user.username)
			markup = types.ReplyKeyboardRemove(selective=False)
			msg = bot.send_message(message.chat.id, "Ваша анкета успешно удалена.", reply_markup=markup)
		except:
			markup = types.ReplyKeyboardRemove(selective=False)
			msg = bot.send_message(message.chat.id, "Ошибка при удалении.", reply_markup=markup)
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		msg = bot.send_message(message.chat.id, "Отмена удаления анкеты.", reply_markup=markup)


@bot.message_handler(commands=['me'])
def view_own_record(message):
	record = db.find_record(message.from_user.username)
	userdata = {}
	if len(record) != 0:
		found = record[0]
		userdata["name"] = found[2]
		userdata["last_name"] = found[3]
		userdata["age"] = found[4]
		msg = bot.send_message(message.chat.id, f'Ваша анкета:\nИмя: {userdata["name"]}\nФамилия: {userdata["last_name"]}\nВозраст: {userdata["age"]}\n')
	else:
		msg = bot.send_message(message.chat.id, "Вашей анкеты еще нету в базе данных!")

@bot.message_handler(commands=['users'])
def view_all_records(message):
	text = "Пользователи в базе данных:\n"
	records = db.query_all()
	if len(records) != 0:
		for record in records:
			text += f"{record[1]}\n" 
		msg = bot.send_message(message.chat.id, text)
	else:
		msg = bot.send_message(message.chat.id, "Зарегестрированных пользователей еще нет.")
	

@bot.message_handler(commands=['update'])
def update_own_record_prompt(message):
	record = db.find_record(message.from_user.username)
	userdata = {}
	if len(record) != 0:
		found = record[0]
		userdata["name"] = found[2]
		userdata["last_name"] = found[3]
		userdata["age"] = found[4]
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
		y_button = types.KeyboardButton('Да')
		n_button = types.KeyboardButton('Нет')
		markup.add(y_button, n_button)
		msg = bot.send_message(message.chat.id, f'Ваша предыдущая анкета:\nИмя: {userdata["name"]}\nФамилия: {userdata["last_name"]}\nВозраст: {userdata["age"]}\nИзменить?', reply_markup=markup)
		bot.register_next_step_handler(msg, update_own_record)
	else:
		msg = bot.send_message(message.chat.id, "Вашей анкеты еще нету в базе данных!")

def update_own_record(message):
	if message.text == "Да":
		markup = types.ReplyKeyboardRemove(selective=False)
		msg = bot.send_message(message.chat.id, "Введите новое имя.", reply_markup=markup)
		savedata["username"] = message.from_user.username
		bot.register_next_step_handler(msg, upd_process_name)
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		msg = bot.send_message(message.chat.id, "Отмена обновления анкеты.", reply_markup=markup)

def upd_process_name(message):
	try:
		if validate_string(message.text):
			savedata["name"] = message.text
			msg = bot.send_message(message.chat.id, "Введите новую фамилию.")
			bot.register_next_step_handler(msg, upd_process_last_name)
		else:
			msg = bot.send_message(message.chat.id, "Введите имя. Оно должно содержать только буквы, и никаких знаков и цифр.")
			bot.register_next_step_handler(msg, upd_process_name)
	except Exception as e:
		bot.reply_to(message, e)

def upd_process_last_name(message):
	try:
		if validate_string(message.text):
			savedata["last_name"] = message.text
			msg = bot.send_message(message.chat.id, "Введите новый возраст.")
			bot.register_next_step_handler(msg, upd_process_age)
		else:
			msg = bot.send_message(message.chat.id, "Введите фамилию. Она должна содержать только буквы, и никаких знаков и цифр.")
			bot.register_next_step_handler(msg, upd_process_last_name)
	except Exception as e:
		bot.reply_to(message, e)


def upd_process_age(message):
	try:
		if validate_digits(message.text):
			savedata["age"] = message.text
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
			y_button = types.KeyboardButton('Да')
			n_button = types.KeyboardButton('Нет')
			markup.add(y_button, n_button)
			msg = bot.send_message(message.chat.id, f'Ваша анкета: \nИмя: {savedata["name"]} \nФамилия: {savedata["last_name"]} \nВозраст: {savedata["age"]}\nСохранить?', reply_markup=markup)
			bot.register_next_step_handler(msg, upd_process_update)
		else:
			msg = bot.send_message(message.chat.id, "Введите возраст. Он должен содержать лишь цифры.")
			bot.register_next_step_handler(msg, upd_process_age)
	except Exception as e:
		bot.reply_to(message, e)


def upd_process_update(message):
	if message.text == "Да":
		username = savedata["username"]
		name = savedata["name"]
		surname = savedata["last_name"]
		age = savedata["age"]

		try:
			db.update_record(username, name, surname, age)
			markup = types.ReplyKeyboardRemove(selective=False)
			msg = bot.send_message(message.chat.id, "Ваши данные успешно изменены.", reply_markup=markup)
		except Exception as e:
			print(e)
			# markup = types.ReplyKeyboardRemove(selective=False)
			# msg = bot.send_message(message.chat.id, "Вы уже зарегестрированы в нашей базе данных.", reply_markup=markup)
	elif message.text == "Нет":
		markup = types.ReplyKeyboardRemove(selective=False)
		msg = bot.send_message(message.chat.id, "Отмена обновления анкеты.", reply_markup=markup)

bot.polling(none_stop=True)