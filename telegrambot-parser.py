from aiogram import Bot,Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from bs4 import BeautifulSoup
import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os
from dotenv import load_dotenv
load_dotenv()
bot = Bot(token=os.getenv("API_TOKEN"))
dp = Dispatcher()
parsing_state = False
@dp.message(Command(commands=["start"]))
async def start_process(msg:Message):
    
    parse_btn = KeyboardButton(text="начать")
    stop_btn = KeyboardButton(text="стоп")
    keyboard = ReplyKeyboardMarkup(keyboard=[[parse_btn, stop_btn]], resize_keyboard=True)
    await msg.answer("все четко я тут",reply_markup=keyboard)

@dp.message(lambda message: message.text == "/parse" or message.text == "начать")
async def parse_process(msg:Message):
    global parsing_state,total_results
    if parsing_state == False:
        parsing_state = True
        total_results = 0
        link = "https://auto.drom.ru/lexus/all/"
        while parsing_state:
            response = requests.get(link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text,"html.parser")
                car_title = soup.find_all("div", class_="css-l1wt7n e3f4v4l2")
                price = soup.find_all("span", class_="css-46itwz e162wx9x0")
                price_quality = soup.find_all("div", class_="css-11m58oj evjskuu0")
                total_results += len(car_title)
                car_link = soup.find_all("a",class_="css-xb5nz8 e1huvdhj1")

                for car_title_text, price_text,car_link_text,price_quality_text in zip(car_title,price,car_link,price_quality):
                    print(car_title_text.text, "  |||   ", price_text.text,"  |||   ",price_quality_text.text, "  ||| ", car_link_text.get("href"))
                    href = car_link_text.get("href")
                    result = f"{car_title_text.text} ||| {price_text.text} ||| {price_quality_text.text} ||| {href}"
                    await msg.answer(result)
                next_page = soup.find("a",class_='css-4gbnjj e24vrp30')
                if next_page:
                    link = next_page.get("href")
                else: 
                    print("no more pages")
            else:
                print("error")
    else:
        msg.answer("parsing in process")

@dp.message(lambda message: message.text == "/stop" or message.text == "стоп")
async def stop_parse_process(msg:Message):
    global parsing_state
    if parsing_state:
        parsing_state = False
        for i in range(15):
            await msg.answer(f"парсинг остановлен, спаршенно {total_results} объявлений")
    else:
        await msg.answer("парсинг не активен")

if __name__ == "__main__":
    dp.run_polling(bot)