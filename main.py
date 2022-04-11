
import time
import requests
from PIL import Image, ImageFont, ImageDraw
from aiogram import Bot, types
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton
from aiogram.types import ChatActions
from bs4 import BeautifulSoup
import asyncio
import psycopg2

bot = Bot('5228894899:AAF3LWfOD-OEKofwGxM9b-xu7OCE07domC8')
dp = Dispatcher(bot, storage=MemoryStorage())


async def anti_flood(*args, **kwargs):
    m = args[0]
    await m.answer("Пожалуйста не спамь, мне придется заблокировать тебя на некоторое время)")
    time.sleep(3)
    await m.answer("Воспользуйся кнопками, если тебе что-то непонятно напиши /help")
    await bot.delete_webhook(drop_pending_updates=True)


class FSMplayer(StatesGroup):
    player_name = State()
    call_msg = State()


@dp.message_handler(commands=['start', 'help'])
async def start_msg(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reply_but = KeyboardButton('/Поиск_футболиста')
    keyboard.add(reply_but)
    await bot.send_message(message.chat.id,
                           f"""Здраствуй, {message.chat.first_name},
Я футбольный бот и я умею показывать актуальную стоимость и другую полезную информацию о каждом футболисте, 
попробуй сам!
Инструкция:
•Нажмите кнопку /Поиск_футболиста или введите вручную чтобы начать поиск игрока, 
введите полное или хотя бы частичное имя или фамилию футболиста, например:"Cristiano Ronaldo, Pedri, Foden".
•Если поиск не дал результатов, то попробуйте заменить язык вввода, например: "Вместо Роналдо напишите Ronaldo", 
также не забывайте что фамилии русских игроков лучше писать русскими буквами, 
а фамилии иностранных - латинскими буквами.
Надеюсь я буду вам полезен!
"""
                           ,
                           reply_markup=keyboard)
    DB_URL = 'postgres://hckxwdjshttado:9dfe7557d68d114e9b6bac4c188fcce55f9fc8880dec12dc9022c25cc0894a68@ec2-52-18-116-67.eu-west-1.compute.amazonaws.com:5432/dp5c450sd3he3'
    connect = psycopg2.connect(DB_URL, sslmode="require")
    cursor = connect.cursor()
    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM users WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        user = [message.chat.id, message.chat.first_name]
        cursor.execute("INSERT INTO users VALUES(%s, %s);", user)
        connect.commit()


@dp.message_handler(commands='Поиск_футболиста')
async def name(message: types.Message):
    await message.answer('Введите полное имя футболиста')
    await FSMplayer.player_name.set()

@dp.message_handler(commands='Пабло5626')
async def secret(message: types.Message):
    try:
        secret_photo = requests.get('https://www.meme-arsenal.com/memes/db542c668fd88cc5cc3d2a9c7a28567a.jpg')
        secret_jpg = open('secret.jpg', 'wb')
        secret_jpg.write(secret_photo.content)
        secret_jpg.close()
        secret_send = open('secret.jpg', 'rb')
        await bot.send_photo(chat_id=message.chat.id, photo=secret_send)
    except Exception as e:
        print(e)


@dp.message_handler()
@dp.throttled(anti_flood, rate=2)
async def main(message: types.Message):
    await message.answer(
        f"К сожалению такой команды нет: {message.text}\nПопробуй написать /help если ты не разобрался как пользоваться ботом")



@dp.message_handler(state=FSMplayer.player_name)
async def search_player(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['player_name'] = message.text
        global text6
        text6 = data['player_name']
        list1 = []
        list2 = []
        list3 = []
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
        page = 'https://www.transfermarkt.ru/schnellsuche/ergebnis/schnellsuche?query=' + str(data['player_name'])
        pageTree = requests.get(page, headers=headers)
        soup = BeautifulSoup(pageTree.content, 'lxml')
        info = soup.find_all('td', class_='zentriert')
        club = soup.find_all('img', class_='tiny_wappen')
        price = soup.find_all('td', class_='rechts hauptlink')

        searching_res = soup.find('div', class_='table-header')
        for i2 in club:
            list2.append(i2.get('alt'))
        for i3 in price:
            list3.append(i3.text)
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        await asyncio.sleep(1)
        await message.answer(searching_res.text.replace('                    ', ''))
        for i in soup.select("td[class='hauptlink']", limit=1):
            keyboard_inl = types.InlineKeyboardMarkup()
            keyboard_inl.add(types.InlineKeyboardButton(text="Показать полную информацию", callback_data='show'))
            await message.answer(i.text + "\n" + str('Амплуа: ' + info[0].text) + " " + str(info[1].text) + "\n" + str(
                "Возраст: " + info[2].text) + '\n' + ("Клуб: " + list2[0]) + '\n' + ("Стоимость: " + list3[0]),
                                 reply_markup=keyboard_inl)
            del info[0:4]
            del list2[0]
            del list3[0]
        await state.finish()
    except Exception as e:
        print(e)
        await message.answer(
            "Такого футболиста не существует или были введены неправильные данные поиска" + '\n' + 'Попробуйте еще раз:')


@dp.callback_query_handler(text="show")
async def send_random_value(call: types.CallbackQuery):
    try:
        c = 0
        if c >= 1:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        name_for_par = []
        global text3
        text3 = call.message.text
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
        page = 'https://www.transfermarkt.ru/schnellsuche/ergebnis/schnellsuche?query=' + text6
        pageTree = requests.get(page, headers=headers)
        soup = BeautifulSoup(pageTree.content, 'lxml')
        for i in soup.select("td[class='hauptlink']", limit=7):
            if i.text in text3:
                name_for_par.append(i.text)
        the_right_pl = soup.find('td', class_='hauptlink', text=name_for_par[0]).find('a')
        global page2
        get_href = the_right_pl.get('href')
        page2 = 'https://www.transfermarkt.ru' + get_href
        pageTree = requests.get(page2, headers=headers)
        soup = BeautifulSoup(pageTree.content, 'lxml')
        nationality = soup.find('span', itemprop='nationality')
        growth = soup.find('span', itemprop='height')
        name_full = soup.find_all('span', class_='info-table__content info-table__content--bold')
        agent = soup.find_all('span', class_='info-table__content info-table__content--regular')

        url_receiving = soup.find('div', class_='data-header__profile-container').find('img')
        get_url = url_receiving.get('src')
        img = requests.get(get_url)
        img_open = open('Player3.jpg', 'wb')
        img_open.write(img.content)
        img_open.close()
        background = requests.get(
            'https://thumb.tildacdn.com/tild6536-3238-4531-a131-353263313330/-/resize/824x/-/format/webp/7.jpg')
        backgr_open = open('background.jpg', 'wb')
        backgr_open.write(background.content)
        backgr_open.close()

        im1 = Image.open('background.jpg')
        im2 = Image.open('Player3.jpg')
        size = (1080, 1080)
        resize = im1.resize(size)
        size2 = (208, 271)
        resize2 = im2.resize(size2)
        resize.paste(resize2, (3, 3))
        resize.save('Gotovo.jpg', quality=95)
        resize.close()
        im2.close()
        image = Image.open('Gotovo.jpg')
        font = ImageFont.truetype('Alt.ttf', 30)
        drawer = ImageDraw.Draw(image)
        fill = "#63389c"
        span = soup.find_all('span', class_='info-table__content')
        spisok = []
        for i in span:
            spisok.append(i.text.strip().replace('\n', ''))
        delemiter = '\n'
        before_replace = delemiter.join(spisok)
        replace_spisok = before_replace.replace(':\n', ': ')
        drawer.text((225, 3), replace_spisok,
                    font=font, fill=fill)
        image.save('Final2.jpg')
        new_image2 = open('Final2.jpg', 'rb')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data='brie'))
        await bot.send_chat_action(call.message.chat.id, ChatActions.UPLOAD_PHOTO)
        await asyncio.sleep(1)
        await bot.send_photo(chat_id=call.message.chat.id, photo=new_image2, reply_markup=keyboard)
        c += 1
    except Exception as e:
        print(e)
        await call.message.answer(
            f"К сожалению не удалось найти полную информацию о данном игроке, при желании вы можете посмотреть ее здесь {page2}")


@dp.callback_query_handler(text='brie')
async def send_random_value_repeat(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    text2 = text3
    keyboard_inl = types.InlineKeyboardMarkup()
    keyboard_inl.add(types.InlineKeyboardButton(text="Показать полную информацию", callback_data='show'))
    await bot.send_chat_action(call.message.chat.id, ChatActions.TYPING)
    await call.message.answer(text2, reply_markup=keyboard_inl)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
