import logging
import sys

from aiogram import Bot, Dispatcher, executor, types

import settings
import yadisk


bot = Bot(token=settings.TG_TOKEN)
dp = Dispatcher(bot)
yd = yadisk.YaDisk(token=settings.YD_TOKEN_test if settings.DEBUG else settings.YD_TOKEN)

image_names = {}


start_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Разрешение")],
        [types.KeyboardButton(text="Фото")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери вид фотки"
)

@dp.message_handler(commands=['start', 'старт'])
async def process_start_command(message: types.Message):
    await message.answer("Привет! Я загружаю фотки на Яндекс Диск. Сначала выбери тип изображения, которое собираешься загрузить.", reply_markup=start_keyboard)

@dp.message_handler(content_types=['text'])
async def name_input(message: types.Message):
    if message.text == "Разрешение":
        image_names[message.from_user.id] = [f'{settings.BASE_DIR}{settings.ALLOWS_DIR}', 0]
        await message.reply("Теперь введи подпись для этого разрешения", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Фото":
        image_names[message.from_user.id] = [f'{settings.BASE_DIR}{settings.PHOTOS_DIR}', 0]
        await message.reply("Теперь введи подпись для этого фото", reply_markup=types.ReplyKeyboardRemove())
    else:
        image_names[message.from_user.id][0] += message.text
        await message.reply("Хорошо, теперь, пришли изображение")

@dp.message_handler(content_types=['document', 'photo']) # получаем фото доком
async def handle_image(message: types.Message):
    await bot.send_message(message.from_user.id, "Загружаю...")
    try:
        photo = message.photo[-1] if message.photo else message.document
        print(photo)
        file_id = photo.file_id if message.photo else message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        extension = file_path.split('.')[-1]
        # ------------Вариант 1 загрузки файлов на диск-------------------
        ## await bot.download_file(file_path, os.path.join('Download', message.document.file_name))
        # ------------Вариант 2 загрузки файлов в яндекс-облако------------
        # пути
        src = f'{message.from_user.id} - Путь не задан'
        if image_names[message.from_user.id]:
            i = f'_{image_names[message.from_user.id][1]}' if image_names[message.from_user.id][1] else ''
            src = image_names[message.from_user.id][0] + i + f'.{extension}'
        logging.debug(src)
        image_names[message.from_user.id][1] += 1
        yd.upload(await bot.download_file(file_path), src)
        await message.answer(f'Всё, загрузил {src.split("/")[-1]} в {"/".join(src.split("/")[:-1])}', reply_markup=start_keyboard)
    except Exception as e:
        logging.error(e)
        await message.answer(f'Ошибка при загрузке {e}', reply_markup=start_keyboard)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    executor.start_polling(dp)