import telebot
from types import SimpleNamespace
from bs4 import BeautifulSoup
import requests

token = ""
bot = telebot.TeleBot(token)
wh_id = ['2042899865']

@bot.message_handler(commands=['start'])
def start(message):
    if str(message.chat.id) in wh_id:
        print("AUTHORIZED:", message.chat.id)
        bot.send_message(message.chat.id, message.text)
    else:
        print("UNAUTHORIZED:", message.chat.id)
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")

@bot.message_handler(content_types=['text'])
def art_find(message):
    if str(message.chat.id) in wh_id:
        print("AUTHORIZED:", message.chat.id)

        art = message.text.strip()
        base_url = f"https://alm-basket-cdn-02.geobasket.ru/vol{art[0:4]}/part{art[0:6]}/{art}"

        info_url = f"{base_url}/info/ru/card.json"
        response = requests.get(info_url)
        if response.status_code == 200:
            data = response.json()
            bot.send_message(message.chat.id, f" {data.get('imt_name', 'Название недоступно')}")
            bot.send_message(message.chat.id, f" Артикул: {data.get('imt_id', 'Артикул недоступен')}")
            bot.send_message(message.chat.id, f" Цвет: {data.get('nm_colors_names', 'цвет недоступен')}")
            bot.send_message(message.chat.id, f" Описание: {data.get('description', 'Описание недоступно')}")
            bot.send_message(message.chat.id, f" Тип: {data.get('subj_name', 'Тип недоступен')}")
            bot.send_message(message.chat.id, f" Бренд: {data.get('selling', 'Бренд недоступен')['brand_name']}")
        else:
            bot.send_message(message.chat.id, " Не удалось получить информацию о товаре.")
            return

        


        price_url = f"{base_url}/info/price-history.json"
        response_2 = requests.get(price_url)
        if response_2.status_code == 200:
            data_2 = response_2.json()


            prices = []
            for item in data_2:
                try:
                    rub_price = item["price"]["RUB"] // 100 
                    exchange_rate = 6.4
                    tg_price = rub_price* exchange_rate
                    prices.append(round(tg_price))
                except (KeyError, TypeError):
                    continue

            if prices:
                current_price = prices[-1]
                avg_price = sum(prices) / len(prices)
                level=''
                if current_price < avg_price:
                    level = "Цена ниже средней"
                elif current_price > avg_price:
                    level = "Цена выше средней"
                else:
                    level = "Цена равна средней"
                bot.send_message(message.chat.id, (
                    f" Средняя цена: {round(avg_price)}₸\n"
                    f" Текущая цена: {current_price}₸"
                    f"\n Уровень цены: {level}"
                ))
            else:
                bot.send_message(message.chat.id, " История цен пуста или в неверном формате.")
        else:
            bot.send_message(message.chat.id, " Не удалось получить историю цен.")
        reviews_url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=269&spp=30&hide_dtype=13&ab_testing=false&lang=ru&nm=93106698;{art}"
        response_3 = requests.get(reviews_url)
        if response_3.status_code == 200:
            data_3 = response_3.json()
            bot.send_message(message.chat.id, f" Количество отзывов: {data_3['data']['products'][0]['feedbacks']}")
            bot.send_message(message.chat.id, f" Средняя оценка: {data_3['data']['products'][0]['reviewRating']}")
        else:
            bot.send_message(message.chat.id, " Не удалось получить отзывы.")
    else:
        print("UNAUTHORIZED:", message.chat.id)
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")



if __name__ == "__main__":
    bot.infinity_polling()

