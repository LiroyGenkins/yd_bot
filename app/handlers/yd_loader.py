import logging
import yadisk
import settings

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.keyboards import photo_keyboard, cancel_keyboard, start_keyboard, loaded_keyboard

# подключение к ЯД
yd = yadisk.YaDisk(token=settings.YD_TOKEN_test if settings.DEBUG else settings.YD_TOKEN)
nums = {}


class LoadPhoto(StatesGroup):
    waiting_for_photo_type = State()
    waiting_for_photo_name = State()
    waiting_for_photo_files = State()


async def load_start(message: types.Message, state: FSMContext):
    await message.answer("Выбери тип фотки", reply_markup=photo_keyboard)
    await state.set_state(LoadPhoto.waiting_for_photo_type.state)


async def type_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_type=message.text.lower())
    # определяем базовые пути
    if message.text == "Разрешение":
        await state.update_data(chosen_dir=f'{settings.BASE_DIR}{settings.ALLOWS_DIR}')
        nums[message.from_user.id] = 0
        await message.reply("Теперь введи подпись для этого разрешения", reply_markup=cancel_keyboard)
    elif message.text == "Фото":
        await state.update_data(chosen_dir=f'{settings.BASE_DIR}{settings.PHOTOS_DIR}')
        nums[message.from_user.id] = 1
        await message.reply("Теперь введи подпись для этого фото", reply_markup=cancel_keyboard)
    await state.set_state(LoadPhoto.waiting_for_photo_name.state)


async def name_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_name=message.text.lower())
    await message.answer("Хорошо, теперь, пришли изображения и когда все загрузятся нажми на кнопу Больше нет фото",
                         reply_markup=loaded_keyboard)
    await state.set_state(LoadPhoto.waiting_for_photo_files.state)


async def file_chosen(message: types.Message, state: FSMContext, bot_obj: Bot):
    # мб message: types.File
    if message.photo or message.document:
        await message.answer("Загружаю...")
        user_data = await state.get_data()
        logging.info(f"ыыыыыы {user_data}")
        try:
            # получаем файл
            photo = message.photo[-1] if message.photo else message.document
            file_id = photo.file_id if message.photo else message.document.file_id
            file = await bot_obj.get_file(file_id)
            file_path = file.file_path
            extension = file_path.split('.')[-1]

            # ------------Вариант 1 загрузки файлов на диск-------------------
            # await bot.download_file(file_path, os.path.join('Download', message.document.file_name))
            # ------------Вариант 2 загрузки файлов в яндекс-облако------------

            # добавляем к пути цифру и расширение
            enum = f"_{nums[message.from_user.id]}" if nums[message.from_user.id] else ''
            # если разрешение(а оно всегда одно) цифру не добавляем
            src = user_data['chosen_dir'] + user_data['chosen_name'] + enum + f'.{extension}'
            logging.info(f'ID:{message.from_user.id} {user_data} {src}')
            nums[message.from_user.id] += 1

            # загружаем
            # yd.upload(await bot_obj.download_file(file_path), src)
            await message.answer(f"Всё, загрузил {user_data['chosen_name']} в {src}")
            logging.info(f"загрузил {user_data['chosen_name']} в {src}")
        except Exception as e:
            logging.error(e)
            await message.answer(f'Ошибка при загрузке {e}')
    elif message.text == "Больше нет фото":
        await state.finish()
        await message.answer("Загрузку окончил", reply_markup=start_keyboard)


# Замыкание для передачи объекта бота
def file_handler(bot_obj):
    async def handler(message, state):
        await file_chosen(message, state, bot_obj)

    return handler


def register_handlers_yd_loader(dp: Dispatcher, bot: Bot):
    dp.register_message_handler(load_start, commands="load", state="*")
    dp.register_message_handler(load_start, Text(equals='Фото или разрешение', ignore_case=True), state="*")
    dp.register_message_handler(type_chosen, state=LoadPhoto.waiting_for_photo_type)
    dp.register_message_handler(name_chosen, state=LoadPhoto.waiting_for_photo_name)
    dp.register_message_handler(file_handler(bot), content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT, types.ContentType.TEXT], state=LoadPhoto.waiting_for_photo_files)
