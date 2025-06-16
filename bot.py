import telebot
from types import SimpleNamespace
from bs4 import BeautifulSoup
import requests
import config

token = config.token
bot = telebot.TeleBot(token)
wh_id = config.wh_id


@bot.message_handler(commands=['start'])
def start(message):
    if str(message.chat.id) in wh_id:
        print("AUTHORIZED:", message.chat.id)
        bot.send_message(message.chat.id, message.text)
    else:
        print("UNAUTHORIZED:", message.chat.id)
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")



def fetch_product_info(art):
    base_url = f"https://alm-basket-cdn-02.geobasket.ru/vol{art[0:4]}/part{art[0:6]}/{art}"
    info_url = f"{base_url}/info/ru/card.json"
    response = requests.get(info_url)
    return response.json() if response.status_code == 200 else None


def fetch_price_history(art):
    base_url = f"https://alm-basket-cdn-02.geobasket.ru/vol{art[0:4]}/part{art[0:6]}/{art}"
    price_url = f"{base_url}/info/price-history.json"
    response = requests.get(price_url)
    return response.json() if response.status_code == 200 else None


def fetch_reviews_and_rating(art):
    reviews_url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=269&spp=30&hide_dtype=13&ab_testing=false&lang=ru&nm=93106698;{art}"
    response = requests.get(reviews_url)
    return response.json() if response.status_code == 200 else None


def fetch_questions(imt_id):
    url_q = f'https://questions.wildberries.ru/api/v1/questions?imtId={imt_id}&take=10&skip=0'
    response = requests.get(url_q)
    return response.json() if response.status_code == 200 else None


def send_product_info(message, data):
    bot.send_message(message.chat.id, f" {data.get('imt_name', 'Название недоступно')}")
    bot.send_message(message.chat.id, f" Артикул: {data.get('imt_id', 'Артикул недоступен')}")
    bot.send_message(message.chat.id, f" Цвет: {data.get('nm_colors_names', 'Цвет недоступен')}")
    bot.send_message(message.chat.id, f" Описание: {data.get('description', 'Описание недоступно')}")
    bot.send_message(message.chat.id, f" Тип: {data.get('subj_name', 'Тип недоступен')}")
    selling = data.get('selling')
    brand_name = selling.get('brand_name', 'Бренд недоступен') if selling else 'Бренд недоступен'
    bot.send_message(message.chat.id, f" Бренд: {brand_name}")


def send_price_analysis(message, price_data):
    prices = []
    for item in price_data:
        try:
            rub_price = item["price"]["RUB"] // 100
            tg_price = rub_price * config.exchange_rate
            prices.append(round(tg_price))
        except (KeyError, TypeError):
            continue

    if prices:
        current_price = prices[-1]
        avg_price = sum(prices) / len(prices)
        level = ("Цена ниже средней" if current_price < avg_price
                 else "Цена выше средней" if current_price > avg_price
                 else "Цена равна средней")
        bot.send_message(message.chat.id,
                         f" Средняя цена: {round(avg_price)}₸\n"
                         f" Текущая цена: {current_price}₸\n"
                         f" Уровень цены: {level}")
    else:
        bot.send_message(message.chat.id, " История цен пуста или в неверном формате.")


def send_reviews(message, review_data):
    try:
        product = review_data['data']['products'][0]
        bot.send_message(message.chat.id, f" Количество отзывов: {product['feedbacks']}")
        bot.send_message(message.chat.id, f" Средняя оценка: {product['reviewRating']}")
    except (IndexError, KeyError):
        bot.send_message(message.chat.id, " Не удалось обработать данные отзывов.")


def send_questions(message, questions_data):
    try:
        for i, q in enumerate(questions_data.get('questions', [])):
            bot.send_message(message.chat.id, f"{i + 1}. Вопрос: {q.get('text')}")
            answer = q.get('answer')
            if answer:
                bot.send_message(message.chat.id, f"{i + 1}. Ответ: {answer.get('text')}")
            else:
                bot.send_message(message.chat.id, f"{i + 1}. Ответа пока нет.")
    except Exception:
        bot.send_message(message.chat.id, " Не удалось обработать вопросы.")




@bot.message_handler(content_types=['text'])
def art_find(message):
    if str(message.chat.id) not in wh_id:
        print("UNAUTHORIZED:", message.chat.id)
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return

    print("AUTHORIZED:", message.chat.id)
    art = message.text.strip()

    product_info = fetch_product_info(art)
    if product_info:
        send_product_info(message, product_info)
    else:
        bot.send_message(message.chat.id, " Не удалось получить информацию о товаре.")
        return

    price_data = fetch_price_history(art)
    if price_data:
        send_price_analysis(message, price_data)
    else:
        bot.send_message(message.chat.id, " Не удалось получить историю цен.")

    review_data = fetch_reviews_and_rating(art)
    if review_data:
        send_reviews(message, review_data)

        imt_id = product_info.get('imt_id')
        if imt_id:
            questions_data = fetch_questions(imt_id)
            if questions_data:
                send_questions(message, questions_data)
    else:
        bot.send_message(message.chat.id, " Не удалось получить отзывы.")



if __name__ == "__main__":
    bot.infinity_polling()
