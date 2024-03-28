import requests
import json
import re
from config import keys, BASE_URL, API_KEY


class APIException(Exception):                                           # исключение для ошибок пользователя
    pass


class CurrencyConvertor:

    @staticmethod
    def format_input(values: list):
        '''Обработка ввода пользователя
        3 варианта: 3 параметра(количество, валюта 1, валюта 2),
                    2 параметра - количество, валюта или валюта, количество;
                      в этом случае предполагается цена валюты в рублях
                      или авлюта1 , валюта2 - тогда цена 1 ед. валюты1 в валюте2
                    1 параметр - количество или валюта,
                      если количество - то предполагается доллары в рублях,
                      если валюта - 1 единица валюты в рублях
        валюту разрешается вводить в виде наименования(можно частично),
        либо валютный тикер (USD, EUR и т.д., регистр неважен), причем можно сочетать'''
        def currency_ticker(value):
            '''Внутренняя функция получения валютного тикера и наименования валюты,
             используется только внутри format_input()'''
            if re.search('[A-Za-z]', value) is not None:                             # вариант тикера (латинские буквы)
                value = value.upper()                                                # приводим к верхнему регистру
                if value in keys.values():                                            # есть ли тикер в словаре
                    ticker = value                                                        # фиксируем тикер
                    currency_name = list(keys.keys())[list(keys.values()).index(value)]  # получение ключа
                                                                                       # (наименование валюты) по тикеру
                else:
                    raise APIException(f'Неверное значение тикера {value}')            # исключение ошибочного тикера
            else:                                                                    # вариант с наименованием валюты
                for key in keys.keys():                                          # поиск по ключам в словаре
                    if value.lower() in key.lower():                             # value входит в ключ
                        currency_name = key                                   # фиксируем наименование валюты
                        ticker = keys[key]                                    # фиксируем тикер
                        break
                else:                                                         # поиск завершен совпадений не найдено
                    raise APIException(f'Неверное значение валюты {value}')   # исключение ошибочной валюты
            return currency_name, ticker

        # основное тело функции

        if len(values) == 3:                                                  # 3 параметра
            try:                                                              # проверка 1-го параметра на числовой тип
                amount = float(values[0])
            except ValueError:                                                # не число
                raise APIException('Неверный формат ввода данных')
            base_currency, base_ticker = currency_ticker(values[1])           # получаем 1-ю валюту
            quote_currency, quote_ticker = currency_ticker(values[2])         # получаем 2-ю валюту

        elif len(values) == 2:                                                # 2 параметра
            if values[0][-1].isdigit():                                       # 1-й параметр - число
                work_amount = values[0]
                work_base_cur = values[1]                                     # запоминаем 1-ю валюту
                work_quote_cur = 'Рубль'                                      # 2-я валюта - рубль
            else:                                                             # 1-й параметр - не число
                work_base_cur = values[0]                                     # запоминаем 1-ю валюту
                if values[1][-1].isdigit():                                   # 2-й параметр - число
                    work_amount = values[1]                                   # запоминаем количество
                    work_quote_cur = 'Рубль'                                  # 2-я валюта - рубль
                else:                                                         # 2-й параметр - не число
                    work_quote_cur = values[1]                                # запоминаем 2-ю валюту
                    work_amount = 1                                           # количество - 1, если две валюты

            try:
                amount = float(work_amount)                                   # пробуем перевести число во float
            except ValueError:                                                # если неудачно - исключение
                raise APIException('Неверное значение количества')

            # количество нормальное, обрабатываем валюты
            base_currency, base_ticker = currency_ticker(work_base_cur)       # получаем 1-ю валюту
            quote_currency, quote_ticker = currency_ticker(work_quote_cur)    # получаем 2-ю валюту

        elif len(values) == 1:                                                # вариант с 1 параметром
            if values[0][-1].isdigit():                                       # если это число
                try:
                    amount = float(values[0])                                         # пробуем перевести число во float
                except ValueError:                                                    # если неудачно - исключение
                    raise APIException(f'Неверный формат ввода данных\n{values[0]}')
                base_currency, base_ticker = 'Доллар', 'USD'                   # если единственный параметр - количество
                quote_currency, quote_ticker = 'Рубль', 'RUB'                # переводим доллары в рубли
            else:                                                            # если это валюта
                base_currency, base_ticker = currency_ticker(values[0])      # получаем ее корректно из словаря
                quote_currency, quote_ticker = 'Рубль', 'RUB'                # 2-я валюта - рубль
                amount = 1                                                   # количество - 1

        return base_currency, base_ticker, quote_currency, quote_ticker, amount

    @staticmethod
    def get_price(base_ticker: str, quote_ticker: str, amount: float):
        if base_ticker == quote_ticker:
            raise APIException(f'Невозможно перевести одинаковые валюты {base_ticker}.')
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}')

        req_string = BASE_URL + '?api_key=' + API_KEY + '&from=' +\
            base_ticker + '&to=' + quote_ticker + '&amount=' + str(amount) + '&format=json'
        r = requests.get(req_string)
        rez = json.loads(r.content)
        result = rez['rates'][quote_ticker]['rate_for_amount']

        return result
