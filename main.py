import logging
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
ENV_LOG_LEVEL = "LOG_LEVEL"

START_URL = "https://tevis.ekom21.de/stdar/select2?md=4"
LOCATION_URL = "https://tevis.ekom21.de/stdar/location?{}=1"
REPO_URL = "https://github.com/mrd0ll4r/darmstadt-city-service-bot"
MAXIMUM_BOT_MESSAGE_LENGTH = 200


# It seems that Telegram does not like long messages from bots.
# In our case this happens if we encounter an error and try to send the
# traceback to a chat for debugging.
def bot_send_message(bot: telebot.TeleBot, chat_id: str, message: str):
    chunks = [message[i:i + MAXIMUM_BOT_MESSAGE_LENGTH] for i in
              range(0, len(message), MAXIMUM_BOT_MESSAGE_LENGTH)]
    logging.debug("Split message into %d chunks", len(chunks))

    for c in chunks:
        try:
            logging.debug("Attempting to send chunk %s", c)
            bot.send_message(chat_id, c)
        except:
            logging.exception("Unable to send message")


def test_bot(bot: telebot.TeleBot, chat_id: str, service_id: str,
             location_id: str):
    me = bot.get_me()
    logging.info(me)
    bot.send_message(chat_id,
                     "🕵️ [Darmstadt City Service Bot]({}) looking for appointments for service {} at location {}".format(
                         REPO_URL,
                         service_id, location_id),
                     parse_mode="MARKDOWN",
                     disable_web_page_preview=True)


def search_for_apointments(bot: telebot.TeleBot, service_id: str, chat_id: str,
                           location_id: str):
    session = requests.Session()

    logging.info("Looking for appointments...")
    try:
        # Get some cookies
        _ = session.get(START_URL)

        # Get more cookies?
        _ = session.get(LOCATION_URL.format(service_id))

        # Find available appointments
        response = session.post(
            LOCATION_URL.format(service_id),
            {
                "loc": location_id,
                "select_location": location_id,
            })
        logging.debug("Got response %s", response.text)

    except:
        logging.exception("Request failed")
        bot_send_message(bot, chat_id,
                         "Unable to search for appointments: " + str(
                             traceback.format_exc()))
        return

    # Filter out server errors instead of spamming the chat
    if 500 <= response.status_code < 600:
        logging.debug("Request failed: %s", response.text)
        return

    if (response.status_code != 200 or
            response.text.find("Es ist ein Fehler aufgetreten") != -1):
        logging.error("Request failed: %s", response.text)
        bot_send_message(bot, chat_id,
                         "Something went wrong :(")
        return

    if (response.text.find(
            "wählen Sie die gewünschte Uhrzeit") != -1 or response.text.find(
            "Kein freier Termin verfügbar") == -1):
        logging.info("Found an appointment")
        bot.send_message(chat_id,
                         "Appointments available, click me: {}".format(
                             START_URL))

    else:
        logging.info("Found no appointments")


if __name__ == '__main__':
    print("This is the Darmstadt City Services bot ({})".format(REPO_URL))
    print("Loading environment...")
    load_dotenv()

    bot_token = os.getenv(ENV_TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv(ENV_TELEGRAM_CHAT_ID)
    service_id = os.getenv(ENV_SERVICE_ID)
    location_id = os.getenv(ENV_LOCATION_ID)
    log_level = os.getenv(ENV_LOG_LEVEL)

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=numeric_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S %z')

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
