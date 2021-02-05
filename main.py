import pymongo
import schedule
import time
import telebot
import requests
from bs4 import BeautifulSoup



def parser():
    collection.drop()#удаляем предыдущие данные

    headers = {'user-agent': 'my-app/0.0.1'}#cловарь заголоков

    links = ['https://www.dvfu.ru/about/rectorate/4915/',
             'https://www.dvfu.ru/about/rectorate/288/',
             'https://www.dvfu.ru/about/rectorate/4925/',
             'https://www.dvfu.ru/about/rectorate/4917/',
             'https://www.dvfu.ru/about/rectorate/32416/',
             'https://www.dvfu.ru/about/rectorate/4921/',
             'https://www.dvfu.ru/about/rectorate/37260',
             'https://www.dvfu.ru/about/rectorate/4923/',
             'https://www.dvfu.ru/about/rectorate/33014/',
             'https://www.dvfu.ru/about/rectorate/4913',
             ]

    for url in links:
        res: requests.Response = requests.get(url, headers=headers) #запрос на эти заголовки
        if res.status_code == 200:
            print('Данные были успешно получены')
            open('page.txt', 'w', encoding='utf-8').write(res.text) #заносится спаршенная страница
            soup = BeautifulSoup(res.text, 'html.parser') #прогон с помощью BS возвращает нам объект "BeatifulSoup" в виде вложенной структуры данных
            prof = soup.find_all('div', class_="author-dolj h3 mt-0 mb-4") #тут например содержится текст "первый проректор"
            FIO = soup.find_all('div', class_="author-name h1")
            room_num = soup.find_all('div', class_="block-address")
            phone = soup.find_all('div', class_="mission mb-4")[0].find_all('div', class_="block-phone")
            mail = soup.find_all('div', class_="mission mb-4")[0].find_all('div', class_="block-email")
            FIO_1 = FIO[0].text.split()#разделяем дальше на имя фамилию и отчество
            second_name = FIO_1[0]
            first_name = FIO_1[1]
            middle_name = FIO_1[2]
            result = {
                'Должность': None,
                'Фамилия': None,
                'Имя': None,
                'Отчество': None,
                'Кабинет': None,
                'Телефон': None,
                'Почта': None
            }
            result['Должность'] = prof[0].text
            result['Фамилия'] = second_name
            result['Имя'] = first_name
            result['Отчество'] = middle_name
            result['Кабинет'] = room_num[0].text
            result['Телефон'] = phone[0].text
            result['Почта'] = mail[0].text
            collection.insert_one(result)

        else:
            print('Err')



connect = pymongo.MongoClient('mongodb+srv://telegabot1:telegabot1@cluster0.jaum8.mongodb.net/PROJECT0?retryWrites=true&w=majority')
DAB = connect.telega #коннектиться по ссылке на кластер и через точку указывается база
collection = DAB['FEFU']
bot = telebot.TeleBot("1278213726:AAG0qBlcliAv9hgqBe6QXhoFUYdkfe_N0S4", parse_mode=None) #инициализируем бота по токену. parse_mode -парсер html разметки
                                                                                     #может искать определённые теги и превращать текст в жирный или курсив

@bot.message_handler(commands=['start']) #декораторы обрабатывают полученные сообщения\комманды
def send_welcome(message): #в функцию мы передаём команду
    bot.reply_to(message, "Введите /worker «должность», чтобы найти работника.")#reply_to пересылает сообщение с ответом на него, а не просто сообщение

@bot.message_handler(commands=['admins'])
def print_sudo(message):
    bot.reply_to(message, 'Список администраторов:')
    bot.send_message(message.chat.id, '354912304')

@bot.message_handler(commands=['edit'])
def send_welcome(message):
    print(message.chat.id)
    if message.chat.id == 354912304:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)#инициализируем кнопки
        itembtn1 = telebot.types.KeyboardButton('Добавить')
        itembtn2 = telebot.types.KeyboardButton('Удалить')
        itembtn3 = telebot.types.KeyboardButton('Изменить')
        itembtn4 = telebot.types.KeyboardButton('Обновить')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
        bot.send_message(message.chat.id, "admin, choose func", reply_markup=markup)
        bot.register_next_step_handler(message, edit)#сюда передаётся сообщ которые хотьм послать и следующий шаг
                                                     #к которому перейдём после ответа пользователя

def edit(message):
    if message.text == 'Добавить':
        bot.send_message(message.chat.id, 'Добавление осуществляется по формату:\nДолжность_Фамилия_Имя_Отчество_Кабинет_Телефон_Почта', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, add_2)

    if message.text == 'Удалить':
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('Фамилия')
        itembtn2 = telebot.types.KeyboardButton('Должность')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "Тег поиска?", reply_markup=markup)
        bot.register_next_step_handler(message, edit_2)
    if message.text == 'Изменить':
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('Фамилия')
        itembtn2 = telebot.types.KeyboardButton('Должность')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "Тег поиска?", reply_markup=markup)
        bot.register_next_step_handler(message, edit_4)
    if message.text == 'Обновить':
        parser()
        bot.send_message(message.chat.id, 'Данные были обновлены')


def add_2(message): #ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
    list = message.text.split('_') #вводим данные, разделяются через нижний пробел
    try:
        result = {
            'Должность': list[0].capitalize(), #capitalize - возвращает копию строки, делая первую букву заглавной
            'Фамилия': list[1].capitalize(),
            'Имя': list[2].capitalize(),
            'Отчество': list[3].capitalize(),
            'Кабинет': list[4].capitalize(),
            'Телефон': list[5].capitalize(),
            'Почта': list[6].capitalize()
        }
        answer = collection.find_one({'Должность': list[0]})
        if list[0] == '': #ПРОВЕРКИ
            bot.send_message(message.chat.id, 'Должность указана неверно.')
        else:
            if list[1] == '':
                bot.send_message(message.chat.id, 'Не может быть пустое значении фамилии.')
            else:
                if answer is None:
                    collection.insert_one(result)
                    bot.send_message(message.chat.id, 'Добавлено!')
                else:
                    bot.send_message(message.chat.id, 'Должность кем-то занята. Невозможно добавить.')
    except IndexError:
        bot.send_message(message.chat.id, 'Недостаточно элементов!')


def edit_2(message): #УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
    if message.text == 'Фамилия':
        bot.send_message(message.chat.id, 'Введите фамилию', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, edit_2_1)

    if message.text == 'Должность':
        bot.send_message(message.chat.id, 'Введите должность', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, edit_2_2)


def edit_2_1(message):
    answer = collection.find_one({"Фамилия": message.text})
    if answer is None:
        bot.reply_to(message, 'Совпадений не найдено! Попробуйте ещё раз')
    else:
        bot.send_message(message.chat.id, answer["Фамилия"] + ' ' + answer["Имя"] + ' ' + answer["Отчество"],
                         reply_markup=telebot.types.ReplyKeyboardRemove()) #remove убирает клавиатуру предыдущую
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('Да')
        itembtn2 = telebot.types.KeyboardButton('Нет')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "Желаете удалить?", reply_markup=markup)
        bot.register_next_step_handler(message, edit_3, answer)


def edit_2_2(message):
    answer = collection.find_one({"Должность": message.text})
    if answer is None:
        bot.reply_to(message, 'Совпадений не найдено! Попробуйте ещё раз')
    else:
        bot.send_message(message.chat.id, answer["Фамилия"] + ' ' + answer["Имя"] + ' ' + answer["Отчество"],
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('Да')
        itembtn2 = telebot.types.KeyboardButton('Нет')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "Желаете удалить?", reply_markup=markup)
        bot.register_next_step_handler(message, edit_3, answer)


def edit_3(message, answer):
    if message.text == 'Да':
        collection.delete_one(answer)
        bot.send_message(message.chat.id, 'Удалено', reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        pass


def edit_4(message): #ИЗМЕНИТЬ ПОЛЬЗОВАТЕЛЯ
    print('Я в пункте 4')
    if message.text == 'Фамилия':
        bot.send_message(message.chat.id, 'Введите фамилию', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, edit_4_1)
    if message.text == 'Должность':
        bot.send_message(message.chat.id, 'Введите должность', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, edit_4_2)


def edit_4_1(message):
    answer = collection.find_one({"Фамилия": message.text})
    if answer is None:
        bot.reply_to(message, 'Совпадений не найдено! Попробуйте ещё раз')
    else:
        mongoID = answer['_id']
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('Должность')
        itembtn2 = telebot.types.KeyboardButton('Фамилия')
        itembtn3 = telebot.types.KeyboardButton('Имя')
        itembtn4 = telebot.types.KeyboardButton('Отчество')
        itembtn5 = telebot.types.KeyboardButton('Кабинет')
        itembtn6 = telebot.types.KeyboardButton('Телефон')
        itembtn7 = telebot.types.KeyboardButton('Почта')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
        bot.send_message(message.chat.id, "Что изменяем?", reply_markup=markup)
        bot.register_next_step_handler(message, edit_6, mongoID)


def edit_4_2(message):
    answer = collection.find_one({"Должность": message.text})
    if answer is None:
        bot.reply_to(message, 'Совпадений не найдено! Попробуйте ещё раз')
    else:
        mongoID = answer['_id']
        # bot.register_next_step_handler(message, edit_5, mongoID)'
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('Должность')
        itembtn2 = telebot.types.KeyboardButton('Фамилия')
        itembtn3 = telebot.types.KeyboardButton('Имя')
        itembtn4 = telebot.types.KeyboardButton('Отчество')
        itembtn5 = telebot.types.KeyboardButton('Кабинет')
        itembtn6 = telebot.types.KeyboardButton('Телефон')
        itembtn7 = telebot.types.KeyboardButton('Почта')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
        bot.send_message(message.chat.id, "Что изменяем?", reply_markup=markup)
        bot.register_next_step_handler(message, edit_6, mongoID)


def edit_5(message, mongoID):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    itembtn1 = telebot.types.KeyboardButton('Должность')
    itembtn2 = telebot.types.KeyboardButton('Фамилия')
    itembtn3 = telebot.types.KeyboardButton('Имя')
    itembtn4 = telebot.types.KeyboardButton('Отчество')
    itembtn5 = telebot.types.KeyboardButton('Кабинет')
    itembtn6 = telebot.types.KeyboardButton('Телефон')
    itembtn7 = telebot.types.KeyboardButton('Почта')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
    bot.send_message(message.chat.id, "Что изменяем?", reply_markup=markup)
    bot.register_next_step_handler(message, edit_6, mongoID)


def edit_6(message, mongoID):
    listik = ['Должность', 'Фамилия', 'Имя', 'Отчество', 'Кабинет', 'Телефон', 'Почта']
    if message.text in listik:
        bot.send_message(message.chat.id, 'Введите новое значение', reply_markup=telebot.types.ReplyKeyboardRemove())
        cat = message.text
        bot.register_next_step_handler(message, edit_6_1, mongoID, cat)
    else:
        bot.reply_to(message, 'Используйте клавиатуру!')


def edit_6_1(message, mongoID, cat):
    if message.text == '':
        bot.send_message(message.chat.id, 'Не может быть пустое значение.')
    else:
        collection.update({'_id': mongoID}, {"$set": {cat: message.text.capitalize()}}, upsert=False)
        bot.send_message(message.chat.id, 'Успешно')


@bot.message_handler(commands=['worker'])
def send_welcome(message):
    newstr = message.text.replace("/worker ", "")
    answer = collection.find_one({"Должность": newstr.capitalize()})
    if answer is None:
        bot.reply_to(message, 'Совпадений не найдено! Попробуйте ещё раз')
    else:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        itembtn1 = telebot.types.KeyboardButton('Вся информация')
        itembtn2 = telebot.types.KeyboardButton('ФИО')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "Что Вас интересует?", reply_markup=markup)
        bot.register_next_step_handler(message, tg_print, answer)


def tg_print(message, answer):
    if message.text == 'ФИО':
        bot.send_message(message.chat.id, answer["Фамилия"] + ' ' + answer["Имя"] + ' ' + answer["Отчество"],
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    elif message.text == 'Вся информация':
        bot.send_message(message.chat.id, answer["Фамилия"] + ' ' + answer["Имя"] + ' ' + answer[
            "Отчество"] + '\n' + 'Кабинет: ' + answer["Кабинет"] + '\n' + 'Телефон: ' + answer[
                             "Телефон"] + '\n' + 'Почта: ' + answer["Почта"],
                         reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['list'])
def send_welcome(message):
    jobs_list = []
    for x in collection.find({}):
        jobs_list.append(x["Должность"])
    bot.send_message(message.chat.id, '\n'.join(jobs_list))


while True:
    bot.polling()#чтобы бот не прекращал работу, по завершении запрашиваемых алгоритмов, а ждал новых команд
    schedule.every().day.at("10:30").do(parser())
