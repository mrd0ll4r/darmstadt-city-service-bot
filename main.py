import datetime
import os
import time
import traceback
from dotenv import load_dotenv
import telebot
import requests

ENV_TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
ENV_TELEGRAM_CHAT_ID = "TELEGRAM_CHAT_ID"
ENV_SERVICE_ID = "SERVICE_ID"
ENV_LOCATION_ID = "LOCATION_ID"
ENV_USER_AGENT = "USER_AGENT"

START_URL = "https://tevis.ekom21.de/stdar/select2?md=4"
SUGGEST_URL = "https://tevis.ekom21.de/stdar/suggest?{}=1"
REPO_URL = "https://github.com/mrd0ll4r/darmstadt-city-service-bot"


def test_bot(bot: telebot.TeleBot, chat_id: str, service_id: str,
             location_id: str):
    me = bot.get_me()
    print(me)
    bot.send_message(chat_id,
                     "🕵️ [Darmstadt City Service Bot]({}) looking for appointments for service {} at location {}".format(
                         REPO_URL,
                         service_id, location_id),
                     parse_mode="MARKDOWN",
                     disable_web_page_preview=True)


def search_for_apointments(bot: telebot.TeleBot, service_id: str, chat_id: str,
                           location_id: str):
    session = requests.Session()

    print("Looking for appointments...")
    try:
        # Get some cookies
        _ = session.get(START_URL)

        # Find available appointments
        response = session.post(
            SUGGEST_URL.format(service_id),
            {
                "loc": location_id,
                "select_location": location_id,
            })

    except:
        bot.send_message(chat_id, "Unable to search for appointments: " + str(
            traceback.format_exc()))
        return

    if (response.status_code != 200 or
            response.text.find("Es ist ein Fehler aufgetreten") != -1):
        bot.send_message(chat_id,
                         "Something went wrong :(")
        print(response.text)
        return

    if response.text.find("Kein freier Termin verfügbar") == -1:
        bot.send_message(chat_id,
                         "Appointments available, click me: {}".format(
                             START_URL))

    else:
        print("No appointments at " + datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"))


if __name__ == '__main__':
    print("This is the Darmstadt City Services bot ({})".format(REPO_URL))
    print("Loading environment...")
    load_dotenv()

    bot_token = os.getenv(ENV_TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv(ENV_TELEGRAM_CHAT_ID)
    service_id = os.getenv(ENV_SERVICE_ID)
    location_id = os.getenv(ENV_LOCATION_ID)

    print("Using bot token {}, will post to chat ID {}".format(bot_token,
                                                               chat_id))
    print("Will search for appointments for service {} at location {}".format(
        service_id, location_id
    ))

    bot = telebot.TeleBot(bot_token)
    test_bot(bot, chat_id, service_id, location_id)

    print("Bot functional, starting to look for appointments...")
    while True:
        search_for_apointments(bot, service_id, chat_id, location_id)
        time.sleep(300)
