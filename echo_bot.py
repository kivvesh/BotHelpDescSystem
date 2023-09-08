import telebot
from telebot import types

import time

bot = telebot.TeleBot("5665489116:AAHgcRN2ByOHqsSMXPr8Yi1o5fHmngwqSqQ",parse_mode=None)

inf = []

@bot.message_handler(commands=['start'])
def send_welcome(message):

    global inf
    while len(inf)!=0:
        time.sleep(1)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.InlineKeyboardButton(text='Добавить организацию')
    btn2 = types.InlineKeyboardButton(text='Добавить сотрудника в организации')
    btn3 = types.InlineKeyboardButton(text='Добавить персону')
    kb.add(btn1,btn2,btn3)
    msg1 = bot.send_message(message.chat.id, text = 'Привет, {0.first_name}! Выберите необходимое действие'.format(message.from_user), reply_markup=kb)
    inf.append('Пользователь - {0.first_name} {0.last_name}'.format(message.from_user))
    bot.register_next_step_handler(msg1,choice)

def choice(message):
    if len(inf)!=1:
        bot.register_next_step_handler(message, choice)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.InlineKeyboardButton(text='Добавить контрагента')
    kb.add(btn1)
    if message.text =='Добавить организацию':
        msg1 = bot.send_message(message.chat.id,'напишите инн организации',reply_markup=kb)
        bot.register_next_step_handler(msg1, check_inn)
    elif message.text =='Добавить сотрудника в организации':
        bot.send_message(message.chat.id, 'напишите инн организации, в которой числится сотрудник')
        bot.register_next_step_handler(message, check_inn)


def check_inn(message):
    global inf
    if len(inf)!=1:
        bot.register_next_step_handler(message, choice)
    if len(message.text)!=10:
        name = bot.send_message(message.chat.id,'ИНН организации некорректен, введите вновь')
        bot.register_next_step_handler(name, check_inn)
    else:
        inf.append(f'ИНН - {message.text}')
        name = bot.send_message(message.chat.id, 'Напишите наименование организации')
        bot.register_next_step_handler(name, name_org)


def name_org(message):
    global inf
    if len(inf)!=2:
        bot.register_next_step_handler(message, choice)
    inf.append(f'Наименование организации - {message.text}')
    bot.send_message('@esed_contact', '\n'.join(inf))
    msg = bot.send_message(message.chat.id, 'Ваша заявка успешно зарегистрировано')
    inf = []
    bot.register_next_step_handler(msg, send_welcome)

bot.polling()

'''
@bot.message_handler(content_types=['text'])
def save_resultat(message):
    global inf
    inf.append(f'Наименование организации - {message.text}')
    bot.send_message('@esed_contact', '\n'.join(inf))
    bot.register_next_step_handler(message, name_org(message))




@bot.message_handler(regexp=r'Добавить организацию')
def check_answer(message):
    bot.send_message(message.chat.id,'Напишите ИНН организации')
    answer('ИНН - ' + message.text)

@bot.message_handler(regexp=r'ИНН')
def answer(message):
    bot.send_message('@esed_contact','123')




name = '';
surname = '';
age = 0;
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "Как тебя зовут?");
        bot.register_next_step_handler(message, get_name); #следующий шаг – функция get_name
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg');

def get_name(message): #получаем фамилию
    global name;
    name = message.text;
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?');
    bot.register_next_step_handler(message, get_surname);

def get_surname(message):
    global surname;
    surname = message.text;
    bot.send_message(message.from_user.id,'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age);

def get_age(message):
    global age;
    while age == 0: #проверяем что возраст изменился
        try:
             age = int(message.text) #проверяем, что возраст введен корректно
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста');
        bot.send_message(message.from_user.id, 'Тебе '+str(age)+' лет, тебя зовут '+name+' '+surname+'?')







@bot.message_handler()
def send_welcome(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    btn1 = types.KeyboardButton(text='Добавить организацию')
    btn2 = types.KeyboardButton(text='Добавить сотрудника в организации')
    btn3 = types.KeyboardButton(text='Добавить персону')
    kb.row(btn1,btn2,btn3)
    bot.send_message(message.chat.id,message.text,reply_markup=kb)

@bot.message_handler(regexp=r'Добавить организацию')
def check_answer(message):
    bot.send_message(message.chat.id,'Напишите ИНН организации')
    answer('ИНН - ' + message.text)

@bot.message_handler(regexp=r'ИНН')
def answer(message):
    bot.send_message('@esed_contact','123')
'''

'''
callback кнопка
@bot.message_handler()
def send_welcome(message):
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='кнопка 1',callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text='кнопка 2', callback_data='btn2')
    kb.add(btn1,btn2)
    bot.send_message(message.chat.id,message.text,reply_markup=kb)

@bot.callback_query_handler(func = lambda callback:callback.data)
def check_callback_data(callback):
    if callback.data == 'btn1':
        bot.send_message(callback.message.chat.id,'нажали на 1 кнопку')
'''


'''
кнопку для подключения чата

@bot.message_handler()
def send_welcome(message):
    kb = types.InlineKeyboardMarkup()
    switch = types.InlineKeyboardButton(text='Выбрать чат',switch_inline_query='/start')
    kb.add(switch)
    bot.send_message(message.chat.id,message.text,reply_markup=kb)
'''


'''
кнопки url ссылки
@bot.message_handler()
def send_welcome(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text = 'Кнопка1',url='https://esed.astrobl.ru/')
    btn2 = types.InlineKeyboardButton(text='Кнопка2', url='https://esed.astrobl.ru/')
    kb.add(btn1,btn2)
    bot.send_message(message.chat.id,message.text,reply_markup=kb)
'''
'''
добавление кнопок
@bot.message_handler()
def send_welcome(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    btn1 = types.KeyboardButton(text ='Кнопка1')
    btn2 = types.KeyboardButton(text='Кнопка2')
    kb.add(btn1,btn2)
    bot.send_message(message.chat.id,'Выберите действие',reply_markup=kb)
'''


'''
форматирование сообщений

@bot.message_handler(func= lambda x: True)
def send_welcome(message):
	bot.send_message(message.chat.id,f'Ваш текст - <b>{message.text}</b>',parse_mode='HTML')
'''
'''
удаление сообщений

@bot.message_handler(commands=['start'])
def send_welcome(message):
    message1 = bot.send_message(message.chat.id, message.id)
    time.sleep(3)
    bot.delete_message(message.chat.id,message1.id)
'''

