from aiogram import types


start_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Фото или разрешение")],
        [types.KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери вид загрузки"
)

photo_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Разрешение")],
        [types.KeyboardButton(text="Фото")],
        [types.KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери вид фотки"
)

cancel_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

loaded_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Больше нет фото")]
    ],
    resize_keyboard=True
)

