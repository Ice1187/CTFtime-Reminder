import time
import json
import pytz
import telepot
import requests
from datetime import datetime, timedelta
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

TOKEN = ''
API = 'https://ctftime.org/api/v1/events/?limit={}&start={}&finish={}'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)


class CTF():
    def __init__(self):
        self.title = ''
        self.form = ''
        self.organizner = ''
        self.start_time = ''
        self.end_time = ''
        self.url = ''
        self.weight = 0.0
        self.restrictions = ''

    def set_by_dict(self, arg):
        self.title = arg['title']
        self.form = arg['format']
        # may have multiple organizers
        self.organizner = arg['organizers'][0]['name']
        self.start_time = utc2tz_by_str(arg["start"])
        self.end_time = utc2tz_by_str(arg["finish"])
        self.url = arg["ctftime_url"]
        self.weight = arg["weight"]
        self.restrictions = arg['restrictions']
        return self

    def get_ctf_info(self):
        # formatr string with markdown
        f_info = '*{}*  /  {}\n  - {}  ~  {} (TW)\n  - Official Url: [here]({})\n\n'.format(
            self.title,
            self.form,
            self.start_time,
            self.end_time,
            self.url,
        )
        return f_info


def utc2tz_by_str(time_str):
    tz = pytz.timezone('Asia/Taipei')
    utc = pytz.utc
    time = datetime.strptime(
        time_str, '%Y-%m-%dT%H:%M:%S+00:00').replace(tzinfo=utc).astimezone(tz)
    time = time.strftime('%m/%d %H:%M')
    return time


def get_ctftime_content():
    now = datetime.now()
    days = timedelta(days=7)
    timestamp_start = datetime.timestamp(now)
    timestamp_finish = datetime.timestamp(now + days)
    limit = 5
    api = API.format(limit, timestamp_start, timestamp_finish)
    json_content = requests.get(api, headers=HEADERS)
    content = json.loads(json_content.text)
    return content


def on_chat_msg(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print("Chat Msg:", content_type, chat_type, chat_id)
    print(type(msg), msg)
    if content_type == 'text':
        if msg['text'].startswith('/menu'):
            bot.sendMessage(chat_id, "Menu isn't implement yet.")

        elif msg['text'].startswith('/upcoming'):
            ctftime_content = get_ctftime_content()
            ctfs = [CTF().set_by_dict(ctf) for ctf in ctftime_content]
            info = ''
            for ctf in ctfs:
                info += ctf.get_ctf_info()
            bot.sendMessage(chat_id, info, parse_mode='markdown',
                            disable_web_page_preview=True)


def main():
    print("[+] Telepot Bot start.")

    MessageLoop(bot, {'chat': on_chat_msg}).run_as_thread()

    print("[+] Listening...")

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
