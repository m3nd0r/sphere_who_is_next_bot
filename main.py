import logging
import os
import random

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

load_dotenv()

logging.basicConfig(
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = os.environ.get("TOKEN")


employees_dict = {
    0: "Степан Дибров",
    1: "Павел Ламонов",
    2: "Никита Перетолчин",
    3: "Никита Родин",
    4: "Андрей Глазырин",
    5: "Юрий Рузбанов",
    6: "Андрей Бородин",
    7: "Александр Омелаев",
    8: "Григорий Димитриогло",
    9: "Игорь Назаров",
    10: "Иван Куликов",
    11: "Дмитрий Милов",
    12: "Михаил Швец",
    13: "Виктор Фадеев",
    14: "Евгений Александров",
    15: "Роман Королев",
    16: "Владимир Бирюков",
    17: "Сергей Никитин",
    18: "Александр Чванов",
    19: "Артемий Гаврилов",
    20: "Александр Захаров",
    21: "Андрей Беньковский",
    22: "Максим Ронжин",
    23: "Михаил Михайлов",
    24: "Иван Артеменко",
    25: "Виталий Иванов",
    26: "Павел Петропавлов",
}


class Employee:
    def __init__(self, employees_dict: dict):
        self.employees_dict: dict = employees_dict
        self.id: int = random.choice(list(self.employees_dict.keys()))

    @property
    def next_one(self) -> str:
        return (
            self.employees_dict[self.id + 1]
            if self.id != 26
            else "Паша всегда замыкающий🚀"
        )

    @property
    def random_three(self) -> str:
        random_keys = random.sample(list(self.employees_dict), 3)
        return [self.employees_dict[id] for id in random_keys]

    @property
    def selected(self) -> str:
        return self.employees_dict[self.id]


def split_list(data):
    return [data[i : i + 2] for i in range(0, 4, 2)]


def create_answer_keyboard(selected_employee: Employee) -> list:
    # Заполняем рандомными 3 кнопками
    keyboard = []
    for random_employee in selected_employee.random_three:
        keyboard.append(
            InlineKeyboardButton(
                f"{random_employee}",
                callback_data=f"incorrect, {selected_employee.next_one}",
            )
        )
    # Запоминаем правильный ответ
    correct_button: list = [
        InlineKeyboardButton(
            f"{selected_employee.next_one}",
            callback_data=f"correct, {selected_employee.next_one}",
        )
    ]

    keyboard.extend(correct_button)
    random.shuffle(keyboard)

    return split_list(keyboard)


def continue_keyboard() -> list:
    keyboard: list = [
        InlineKeyboardButton(
            "Сыграть ещё раз",
            callback_data=f"continue",
        ),
        InlineKeyboardButton(
            f"Узнать правильный ответ",
            callback_data=f"get_answer",
        ),
    ]
    return split_list(keyboard)


def get_choosen(context: CallbackContext.DEFAULT_TYPE):
    choosen = Employee(employees_dict)
    context.user_data["selected"] = choosen
    return choosen


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    choosen = get_choosen(context)
    keyboard: list = [
        [
            InlineKeyboardButton(
                "Поехали!",
                callback_data=f"continue",
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет!\nТы ДОЛЖЕН знать порядок людей на созвоне!😈",
        reply_markup=reply_markup,
    )


async def button(update: Update, context: CallbackContext.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    data = query.data
    answer = data.split(",")[0]
    keyboard = continue_keyboard()

    if answer == "correct":
        await query.edit_message_text(
            text=f"Правильно!", reply_markup=InlineKeyboardMarkup([[keyboard[0][0]]])
        )  # жду PR приведением к нормальному виду :)
    elif data == "get_answer":
        await query.edit_message_text(
            text=f"Правильный ответ: {context.user_data['selected'].next_one}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif data == "continue":
        choosen = get_choosen(context)
        keyboard = create_answer_keyboard(choosen)
        await query.edit_message_text(
            text=f"Кто следующий за {choosen.selected}?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await query.edit_message_text(
            text=f"Неправильный ответ. Учим матчасть!",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


if __name__ == "__main__":
    application = (
        ApplicationBuilder().token(TOKEN).build()
    )  # не забываем токен корректный вставить

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()
