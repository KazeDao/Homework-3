import telebot
from telebot import types
from Config import keys, TOKEN
from extensions import APIException, Converter

conv_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
buttons = []
for val in keys.keys():
    buttons.append(types.KeyboardButton(val))

conv_markup.add(*buttons)

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def info(message: telebot.types.Message):
    text = 'Приветствую! \nДля начала работы в ручном режиме введите команду боту через пробел в формате:\
\n<имя валюты, чью цену требуется узнать> \
<в какую валюту требуется конвертация> \
<количество переводимой валюты>\nУвидеть список доступных валют: /values\
\nКонвертировать валюту в диалоговом режиме с клавиатурой валют пользователя /convert'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def value(message: telebot.types.Message):
    text = 'Доступные для конвертации валюты'
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)


@bot.message_handler(commands=['convert'])
def question(message: telebot.types.Message):
    text = 'Выберите валюту, из которой требуется конвертация:'
    bot.send_message(message.chat.id, text, reply_markup=conv_markup)
    bot.register_next_step_handler(message, quote_handler)


def quote_handler(message: telebot.types.Message):
    quote = message.text.strip()
    text = 'Выберите валюту, в которую требуется конвертация:'
    bot.send_message(message.chat.id, text, reply_markup=conv_markup)
    bot.register_next_step_handler(message, base_handler, quote)


def base_handler(message: telebot.types.Message, quote):
    base = message.text.strip()
    text = 'Укажите количество конвертируемой валюты:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, quote, base)


def amount_handler(message: telebot.types.Message, quote, base):
    amount = message.text.strip()
    try:
        total_base = Converter.get_price(quote, base, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка в конвертации:\n{e}')
    else:
        text = f'Цена {amount} {quote} в {base} - {total_base}'
        bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    values = message.text.split()
    try:
        if len(values) != 3:
            raise APIException('Неверный запрос или неверное количество параметров!')

        quote, base, amount = values
        total_base = Converter.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка в команде пользователя:\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Неизвестная ошибка, не могу обработать команду:\n{e}')
    else:
        text = f'Цена {amount} {quote} в {base} - {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling()
