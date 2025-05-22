from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(
    KeyboardButton("Просмотр своего аккаунта"),
    KeyboardButton("Посмотреть калории за день")
)
main_keyboard.row(
    KeyboardButton("Сколько ещё надо съесть"),
    KeyboardButton("Прислать фотографию")
)
main_keyboard.row(KeyboardButton("Картинка с прогрессом"))

account_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
account_keyboard.row(KeyboardButton("Просмотр аккаунта"))
account_keyboard.row(
    KeyboardButton("Редактирование имени"),
    KeyboardButton("Редактирование своего максимума калорий")
)
account_keyboard.row(
    KeyboardButton("Редактирование своего максимума БЖУ"),
    KeyboardButton("Назад в меню")
)

photo_action_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
photo_action_keyboard.row(
    KeyboardButton("Посчитать калории"),
    KeyboardButton("Совет")
)
photo_action_keyboard.row(KeyboardButton("Назад в меню"))
