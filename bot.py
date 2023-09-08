import asyncio
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup,InlineKeyboardButton,KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
import os
import datetime


def select_bd(query):#функция для выборки данных из бд
    sqlite_connection = sqlite3.connect('C:/projects/django_otrs/project/db.sqlite3')
    cursor = sqlite_connection.cursor()
    sqlite_select_query = query
    cursor.execute(sqlite_select_query)
    result = cursor.fetchall()
    sqlite_connection.close()
    return result

def insert_bd(query):#функция для внесения данных в бд
    sqlite_connection = sqlite3.connect('C:/projects/django_otrs/project/db.sqlite3')
    cursor = sqlite_connection.cursor()
    sqlite_insert_query = query
    count = cursor.execute(sqlite_insert_query)
    sqlite_connection.commit()
    sqlite_connection.close()

system = select_bd("""
        SELECT name from applications_systems;
       """)


class Form(StatesGroup):# формы статусов
    start = State()#статус начало работы бота
    start_fio = State()#статус ожидании фио от нового юзера
    start_org = State()#статус ожидании орг от нового юзера
    start_tel = State()# статус ожидании номера телефона для нового юзера


    inn_org = State()#статус ожидании инн
    name_org = State()#статус ожидании наименование организации
    send_kanal_org = State()#статус отправки инф в бд и канал

    error = State()

    inn_org_sotr = State()#статус ожидании инн
    fio_sotr = State()#статус ожидании ФИО сотрудника
    dol_sotr = State()#статус ожидании должности
    send_kanal_sotr = State()  # статус отправки инф в бд и канал

    fio_pers = State()#статус ожидании фио персоны
    send_kanal_pers = State()#статус отправки инф в бд и канал

    system = State()
    text_appl = State()
    send_kanal_appl = State()


load_dotenv()

storage = MemoryStorage()#загрузка данных в словарь
bot = Bot(os.getenv('TOKEN'))#создание бота
dp = Dispatcher(bot=bot,storage=storage)#инициализация бота




fin = ReplyKeyboardMarkup(resize_keyboard=True)#создание клавиатуры
fin.add('Отправить заявку')





finish = ReplyKeyboardMarkup(resize_keyboard=True)
finish.add('Создать заявку')

error = ReplyKeyboardMarkup(resize_keyboard=True)
error.add('Да')

systems = ReplyKeyboardMarkup(resize_keyboard=True)
for s in system:
    systems.add(s[0])



@dp.message_handler(text=['Создать заявку'])
@dp.message_handler(text=['Написать новую заявку'])#обработчик команды
@dp.message_handler(text=['◀️ Назад'])#обработчик команды
@dp.message_handler(commands=['start'])#обработчик команды
@dp.message_handler(state=Form.start)
async def cmd_start(message: types.message,state: FSMContext):
    ip = message.from_user.id#получения ip юзера

    await message.answer_sticker('CAACAgIAAxkBAAIFhWTnBvIFxgbG-8HUTmU_3B6ZVRQpAAJlJQACBp4xSHhTYfWaojnOMAQ')#функция отправки стикера
    user = select_bd(f"SELECT first_name,last_name,patronymic FROM applications_applicants where id_user_tel = '{message.from_user.id}' ")#инициализация юзера
    if len(user)==0:# если пользователь впервые
        await state.update_data(id_appl=message.from_user.id)
        await message.answer('Добрый день, Вы еще ни разу не оставляли заявку через бот. Пожалуйста, представьтесь (ФИО полностью)')
        await state.set_state(Form.start_fio)#назначение статуса ожидании фио от юхера
    else:
        await state.finish()
        query = f"""
                SELECT black_list FROM applications_applicants where id_user_tel='{ip}'
            """#проверка находится ли пользователь в чс
        bl = select_bd(query)[0][0]
        if bl == 0:
            await message.answer(f'Добрый день, {user[0][1]} {user[0][0]} {user[0][2]}, в какой системе Вы хотите оставить заявку?',reply_markup = systems)# функция ответа юзеру
        else:
            await message.answer('Добрый день, Вы были заблокированы')#если статус юзера чс, выхводится сообщение


@dp.message_handler(state=Form.start_fio)#обработчик статуса ожидании фио при знакомстве
async def contacts(message:types.Message,state: FSMContext):
    await state.update_data(ФИО_заявителя = message.text)
    await message.answer('Укажите Вашу организацию', reply_markup=finish)
    await state.set_state(Form.start_org)

@dp.message_handler(state=Form.start_org)
async def contacts(message:types.Message,state: FSMContext):
    await state.update_data(Организация = message.text)
    await message.answer('Укажите Ваш рабочий номер телефона', reply_markup=finish)

    await state.set_state(Form.start_tel)

@dp.message_handler(state=Form.start_tel)
async def contacts(message:types.Message,state: FSMContext):
    await state.update_data(Телефон = message.text)
    await state.set_state(Form.start)
    user_data = await state.get_data()
    fio = user_data['ФИО_заявителя']
    fio = fio.split(' ')

    while len(fio) < 3:
        fio.append('')
    query = """
        INSERT INTO `applications_applicants` (first_name, last_name, patronymic, phone, org, id_user_tel,black_list) 
        VALUES
        ('{first_name}', '{last_name}','{patronymic}','{phone}','{org}','{id_user_tel}','{black_list}');  
    """.format(first_name = fio[1],last_name = fio[0],patronymic = fio[2],phone = user_data['Телефон'], org = user_data['Организация'],id_user_tel = user_data['id_appl'],black_list=0)
    insert_bd(query)
    await message.answer('Создать заявку??', reply_markup=finish)

system_except_esed = system.copy()
system_except_esed.pop(0)
@dp.message_handler(text = [s[0] for s in system_except_esed])
async def contacts(message:types.Message,state: FSMContext):
    ip = message.from_user.id  # получения ip юзера
    query = f"""
                    SELECT black_list FROM applications_applicants where id_user_tel='{ip}'
                """
    bl = select_bd(query)[0][0]
    if bl == 0:
        query = f"""
                select id from applications_systems where name ='{message.text}'
            """
        await state.update_data(ИД_системы=select_bd(query)[0][0])
        bt = [
        [
            KeyboardButton('⚙️ Администрирование'),
        ],
        [
            KeyboardButton('🧑🏻‍💻 Техническая поддержка')
        ],
        [
            KeyboardButton('◀️ Назад')
        ]
    ]

        esed = ReplyKeyboardMarkup(keyboard=bt)

        await message.answer('Выберите действие', reply_markup=esed)
    else:
        await message.answer('Добрый день, вы были заблокированы')

@dp.message_handler(text = 'ЕСЭД')
async def contacts(message:types.Message,state: FSMContext):
    ip = message.from_user.id
    query = f"""
                        SELECT black_list FROM applications_applicants where id_user_tel='{ip}'
                    """
    bl = select_bd(query)[0][0]
    if bl == 0:
        query = f"""
        select id from applications_systems where name ='{message.text}'
    """

        await state.update_data(ИД_системы=select_bd(query)[0][0])
        bt = [
        [
            KeyboardButton('🏢 Добавить организацию'),
            KeyboardButton('🧑🏻‍💼 Добавить контакт'),
            KeyboardButton('👤 Добавить персону')
        ],
        [
            KeyboardButton('⚙️ Администрирование'),
            KeyboardButton('🧑🏻‍💻 Техническая поддержка')
        ],
        [
            KeyboardButton('◀️ Назад')
        ]
    ]

        esed = ReplyKeyboardMarkup(keyboard=bt)

        await message.answer('Выберите действие', reply_markup=esed)
    else:
        await message.answer('Добрый день, вы были заблокированы')

@dp.message_handler(text='⚙️ Администрирование')
async def contacts(message:types.Message,state: FSMContext):
    text = os.getenv('TEXT_1')
    await message.answer(text, reply_markup=finish)

    await message.answer_document(
        'BQACAgIAAxkBAAIQIWTt1omHSgZs1vf_yzIDe00dwwIJAAKANAACS-NxS_NswwybmhxEMAQ')  # функция отправки документ


@dp.message_handler(text='🧑🏻‍💻 Техническая поддержка')
async def contacts(message:types.Message,state: FSMContext):
    await message.answer('Опишите подробно причину заявки', reply_markup=finish)
    await state.set_state(Form.text_appl)

@dp.message_handler(state=Form.text_appl)
async def contacts(message: types.Message, state: FSMContext):
    await state.update_data(Текст_проблемы=message.text)
    await message.answer('Отправить заявку?', reply_markup=fin)
    await state.set_state(Form.send_kanal_appl)
@dp.message_handler(state=Form.send_kanal_appl)
async def contacts(message: types.Message, state: FSMContext):
    id_user_tel = message.from_user.id
    user_data = await state.get_data()
    query = f"""
    SELECT id from applications_applicants where id_user_tel = '{message.from_user.id}'
    """
    user = select_bd(query)[0][0]

    query2 = f"""
    INSERT INTO `applications_other_applications` (text, date_created, status, id_appl_id, system_id) 
        VALUES
        ('{user_data['Текст_проблемы']}', '{datetime.datetime.now()}','{False}','{user}','{user_data['ИД_системы']}');
    """
    insert_bd(query2)
    k=''
    for key,value in user_data.items():
        k = k + key + ' - ' + str(value) +'\n'
    await bot.send_message(os.getenv('GROUP_ID'),k)
    query3 = """
        SELECT id from applications_other_applications order by date_created desc limit 1
    """
    id = select_bd(query3)[0][0]
    await state.finish()
    await message.answer(f'Ваша заявка зарегистрирована под №{id}! Ожидайте', reply_markup=finish)


@dp.message_handler(text='🏢 Добавить организацию')
async def contacts(message:types.Message,state: FSMContext):
    await state.update_data(Необходимо = message.text)
    await message.answer('Введите ИНН организации',reply_markup=finish)
    await state.set_state(Form.inn_org)

def check(inn):
    if len(inn)!=10:
        return False
    try:
        inn_int = int(inn)
    except:
        return False
    koaf = [2,4,10,3,5,9,4,6,8]
    proiz = 0
    for key,value in enumerate(inn[:9]):
        proiz = proiz + int(value) * koaf[key]
    if (proiz % 11) % 10 != int(inn[-1]):
        return False
    return True

@dp.message_handler(state=Form.inn_org)
async def contacts(message:types.Message,state: FSMContext):
    if message.text == 'Написать новую заявку':
        await state.finish()
        await message.answer('Создать новую заявку?', reply_markup=finish)
    else:
        await state.update_data(Пользоветель=f'{message.from_user.first_name} {message.from_user.last_name} с ид: {message.from_user.id}')
        if check(message.text) is False:
            await message.answer('ИНН введен некорректно,введите повторно')
            return
        await state.update_data(ИНН_организации =message.text)
        await message.answer('Напишите полное наименование организации: ',reply_markup=finish)
        await state.set_state(Form.name_org)

@dp.message_handler(state=Form.name_org)
async def contacts(message: types.Message, state: FSMContext):
    if message.text == 'Написать новую заявку':
        await state.finish()
        await message.answer('Создать новую заявку?', reply_markup=finish)
    else:
        await state.update_data(Наименование_организации=message.text)
        await message.answer('Отправить заявку?', reply_markup=fin)
        await state.set_state(Form.send_kanal_org)


@dp.message_handler(state=Form.send_kanal_org)
async def contacts(message: types.Message, state: FSMContext):
    id_user_tel = message.from_user.id
    user_data = await state.get_data()
    query = f"""
        SELECT id from applications_applicants where id_user_tel = '{message.from_user.id}'
        """
    user = select_bd(query)[0][0]
    query = f"""
           INSERT INTO `applications_organizations` (name, inn, status, date_created, id_appl_id) 
           VALUES
           ('{user_data['Наименование_организации']}', '{user_data['ИНН_организации']}','{False}','{datetime.datetime.now()}','{user}');  
       """
    insert_bd(query)

    k=''
    for key,value in user_data.items():
        k = k + key + ' - ' + str(value) +'\n'
    await bot.send_message(os.getenv('GROUP_ID'),k)
    await state.finish()
    await message.answer('Ваша заявка зарегистрирована! Ожидайте', reply_markup=finish)

@dp.message_handler(text='🧑🏻‍💼 Добавить контакт')
async def contacts(message:types.Message,state: FSMContext):
    await state.update_data(Необходимо=message.text)
    await message.answer('Введите ИНН организации, в которой необходимо создать контакт',reply_markup=finish)
    await state.set_state(Form.inn_org_sotr)

@dp.message_handler(state=Form.inn_org_sotr)
async def contacts(message:types.Message,state: FSMContext):
    if message.text == 'Написать новую заявку':
        await state.finish()
        await message.answer('Создать новую заявку?', reply_markup=finish)
    else:
        await state.update_data(
        Пользоветель=f'{message.from_user.first_name} {message.from_user.last_name} с ид: {message.from_user.id}'
    )
        if len(message.text)!=10:
            await message.answer('ИНН введен некорректно,введите повторно')
            return
        await state.update_data(ИНН_организации=message.text)
        await message.answer('Напишите ФИО сотрудника (полностью или в формате: Фамилия И. О.): ',reply_markup=finish)
        await state.set_state(Form.fio_sotr)

@dp.message_handler(state=Form.fio_sotr)
async def contacts(message:types.Message,state: FSMContext):
    if message.text == 'Написать новую заявку':
        await state.finish()
        await message.answer('Создать новую заявку?', reply_markup=finish)
    else:
        await state.update_data(ФИО=message.text)
        await message.answer('Укажите должность (полностью) ',reply_markup=finish)
        await state.set_state(Form.dol_sotr)

@dp.message_handler(state=Form.dol_sotr)
async def contacts(message: types.Message, state: FSMContext):
    if message.text == 'Написать новую заявку':
        await state.finish()
        await message.answer('Создать новую заявку?', reply_markup=finish)
    else:
        await state.update_data(Должность=message.text)
        await message.answer('Отправить заявку?', reply_markup=fin)
        await state.set_state(Form.send_kanal_sotr)

@dp.message_handler(state=Form.send_kanal_sotr)
async def contacts(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    fio = user_data['ФИО']
    fio = fio.split(' ')
    while len(fio)<3:
        fio.append('')
    first_name,last_name,patronymic = fio[1], fio[0], fio[2]
    inn = user_data['ИНН_организации']
    post = user_data['Должность']
    query = f"""
            SELECT id from applications_applicants where id_user_tel = '{message.from_user.id}'
            """
    user = select_bd(query)[0][0]
    query = f"""
               INSERT INTO `applications_contact` (first_name, last_name, patronymic, status, date_created, inn, post, id_appl_id) 
               VALUES
               ('{first_name}', '{last_name}','{patronymic}','{False}','{datetime.datetime.now()}','{inn}','{post}','{user}');  
           """
    insert_bd(query)
    k=''
    for key,value in user_data.items():
        k = k + key + ' - ' + str(value) +'\n'
    await bot.send_message(os.getenv('GROUP_ID'),k)
    await state.finish()
    await message.answer('Ваша заявка зарегистрирована! Ожидайте', reply_markup=finish)
@dp.message_handler(text='👤 Добавить персону')
async def contacts(message:types.Message,state: FSMContext):
    await state.update_data(Необходимо=message.text)
    await message.answer('Напишите ФИО персоны (полностью или в формате: Фамилия И. О.)')
    await state.set_state(Form.fio_pers)

@dp.message_handler(state=Form.fio_pers)
async def contacts(message: types.Message, state: FSMContext):
    await state.update_data(
        Пользоветель=f'{message.from_user.first_name} {message.from_user.last_name} с ид: {message.from_user.id}'
    )
    await state.update_data(ФИО=message.text)
    await message.answer('Отправить заявку?', reply_markup=fin)
    await state.set_state(Form.send_kanal_pers)

@dp.message_handler(state=Form.send_kanal_pers)
async def contacts(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    fio = user_data['ФИО']
    fio = fio.split(' ')
    while len(fio)<3:
        fio.append('')
    first_name,last_name,patronymic = fio[1], fio[0], fio[2]
    query = f"""
                SELECT id from applications_applicants where id_user_tel = '{message.from_user.id}'
                """
    user = select_bd(query)[0][0]
    query = f"""
                   INSERT INTO `applications_person` (first_name, last_name, patronymic, status, date_created,  id_appl_id) 
                   VALUES
                   ('{first_name}', '{last_name}','{patronymic}','{False}','{datetime.datetime.now()}','{user}');  
               """
    insert_bd(query)
    k=''
    for key,value in user_data.items():
        k = k + key + ' - ' + str(value) +'\n'
    await bot.send_message(os.getenv('GROUP_ID'),k)
    await state.finish()
    await message.answer('Ваша заявка зарегистрирована! Ожидайте',reply_markup=finish)



@dp.message_handler()
async def answer(message: types.message):
    await message.reply('Нажми /start для написания новой заявки') #функция ответ на сообщение пользователя


'''
#отправить ид стикера и отправка в чат сообщения направленные боту
@dp.message_handler(content_types=['sticker','document','photo'])
async def check_sticker(message: types.Message):
    await message.answer(message.sticker.file_id)
    await bot.forward_message(os.getenv('GROUP_ID'),message.from_user.id,message.message_id) #функция для отправки в чат сообщение направленное в телеграмм-бот
'''

if __name__ == '__main__':
    executor.start_polling(dp)#запуск бота


