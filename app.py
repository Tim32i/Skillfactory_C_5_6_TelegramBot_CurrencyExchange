import telebot
from config import keys, TOKEN
from extensions import APIException, CurrencyConvertor

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def start_help(message: telebot.types.Message):
    text = "Чтобы начать работу введите команду боту в следующем формате:\n\
    <количество валюты> <валюту> <в какую валюту перевести> \n\
    Или <количество> <валюту>\n<валюту> <количество> - выдаст стоимость этой валюты в рублях\n\
    Или <валюту> <в какую валюту перевести> - выдаст стоимость 1 ед. валюты 1 в валюте 2\n\
    Или <количество> - выдаст стоимость долларов в рублях\n\
    валюту можно вводить по имени (можно частично) или валютным тикером (USD, EUR и т.д., регистр неважен)\n\
    Примеры:\n5 евро долл\nиран инд\nдирхам\nUSD Казах\nCAD jpy\n\
    Увидеть список всех доступных валют: /currency"

    bot.reply_to(message, text)


@bot.message_handler(commands=['currency'])
def currency(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key, value in keys.items():
        text = '\n'.join((text, key + ' : ' + value))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:

        values = message.text.split(' ')

        if len(values) > 3:
            raise APIException('Слишком много параметров.')

        base, base_ticker, quote, quote_ticker, amount = CurrencyConvertor.format_input(values)
        total_base = CurrencyConvertor.get_price(base_ticker, quote_ticker, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        text = f'Цена {amount} {base} в {quote} - {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling()
