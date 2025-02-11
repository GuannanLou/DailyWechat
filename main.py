import os
import json
import requests
from datetime import datetime, timedelta

nowtime = datetime.utcnow() + timedelta(hours=8)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")


def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日") + a


def get_words():
    req = requests.get("https://api.shadiao.pro/chp")
    words = req.json()
    print(words)
    if req.status_code != 200:
        return get_words()
    return words['data']['text']

def get_weather(city, key):
    url = f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={city}&language=zh-Hans&unit=c&start=-1&days=5"
    res = requests.get(url).json()
    print(res)
    weather = (res['results'][0])["daily"][0]
    city = (res['results'][0])["location"]["name"]
    return city, weather

def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days


def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days


if __name__ == '__main__':
    weather_key = os.getenv("WEATHER_API_KEY")
    bot_key = os.getenv("BOT_API_KEY")


    f = open("users_info.json", encoding="utf-8")
    js_text = json.load(f)
    f.close()
    user_info = js_text['data'][0]
    data = js_text['data']
    words=get_words()
    out_time=get_time()

    born_date = user_info['born_date']
    birthday = born_date[5:]
    city = user_info['city']
    name = user_info['user_name'].upper()

    wea_city, weather = get_weather(city, weather_key)

    end = ''
    if weather['date'] == '2025-02-12':
        end = '别忘记订酒店和火车票嗷'
    elif weather['date'] == '2025-02-14':
        end = '最后一天，调整好心态嗷，记得检查火车票和考场\n加油！爱您！'
    elif weather['date'] == '2025-02-15':
        end = '莫紧张，祝好姐姐正常发挥'
    elif weather['date'] == '2025-02-16':
        end = '恭喜！！！'
    elif weather['date'] == '2025-02-17':
        end = '收拾收拾心情，小心感冒嗷'

    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(bot_key.replace('_','-'))

    content = """{head} ヾ(≧▽≦*)o

φ(゜▽゜*)♪{name}小盆友

今天是{date}
坐标城市：{city}  
当前天气：{weather}  
当前风力：{wind}级  
今日湿度：{humidity}
今日温度：{tem_low}℃~{tem_high}℃ 

庆祝自己在世界上 第{born_days}天  
距离下次生日还有 {birthday_left}天  

( •̀ ω •́ )✧

今日彩虹屁🌈
{words}

今日MEMO📕
{end}""".format(
        head = "早上好哇！",
        name = name,
        date = "{} {}".format(weather['date'], out_time[-3:]),
        city = wea_city,
        weather = weather['text_day'],
        wind = weather['wind_scale'],
        tem_low = weather['high'],
        tem_high = weather['low'],
        humidity = weather['humidity'],
        born_days = get_count(born_date),
        birthday_left = get_birthday(birthday),
        words = words,
        end = end
    )

    data = {
        "msgtype": "text",
        "text": {
            "content": content,
        }
    }

    res = requests.post(url=url,data=json.dumps(data))
    print(res.text)
