import telebot
from telebot import types
import os
import oauth2client
import oauthlib
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import schedule
import time
from threading import Thread
import sys
from pytube import Playlist

#Переделать кнопку видеоматериалы в тип url
def get_service_sacc():
    creds_json="C:/Users/fov-2/Downloads/studybot-363615-ee1b83df91ea.json"
    scopes=['https://www.googleapis.com/auth/spreadsheets']
    creds_service=ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)
#bot-34@studybot-363615.iam.gserviceaccount.com
def prepare_dop():
    resp=get_service_sacc().spreadsheets().values().batchGet(spreadsheetId="1CECodrbWgAcWQo3JnT27_o0ELpMYMM-hntxAYt5w_Gg", ranges=["Лист1"]).execute()
    new=resp.get("valueRanges")[0].get("values")[1::]
    result=""
    for item in new:
        result+=item[0]+": "+item[1]+"\n"
    return result
def prepare_video():
    playlist='https://youtube.com/playlist?list=PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa'
    urls=""
    i=1
    playlist_urls=Playlist(playlist)
    for url in playlist_urls:
        urls+=str(i)+". "+url+"\n"
        i+=1
    return urls
    

bot = telebot.TeleBot('secret')
FLAG=True
scheduler_on_going=[]
threads=[]

class minute(Thread):
    minutes=0
    userid=""
    def __init__(self, minutes, userId):
        self.minutes=minutes
        self.userid=userId
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        bot = telebot.TeleBot('secret')
        print("minute")
        while FLAG==True:
            time.sleep(self.minutes*60)
            if(FLAG==True):
                bot.send_message(self.userid, "Напоминаем Вам о нашем курсе!")
class hour(Thread):
    hours=0
    userid=""
    def __init__(self, hours, userId):
        self.hours=hours
        self.userid=userId
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        bot = telebot.TeleBot('secret')
        while FLAG==True:
            time.sleep(self.hours*60*60)
            if(FLAG==True):
                bot.send_message(self.userId, "Напоминаем Вам о нашем курсе!")

def scheduler_start():
    print("FLAG:"+str(FLAG))
    file=open('users.txt', 'r')
    for line in file:
        result=line.split(":")
        if(result[0] not in scheduler_on_going):
            scheduler_on_going.append(result[0])
            if(result[2]=="0"):
                minute(int(result[1]), result[0])
                #threads.append(m)
            elif(result[2]=="1"):
                hour(int(result[1]), result[0])
                #threads.append(h)
    file.close()

scheduler_start()
@bot.message_handler(commands=['start'])
def start(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Прошу напоминать об учебе мне раз в 1 минуту.")
    markup.add(item1)
    item2=types.KeyboardButton("Прошу напоминать об учебе мне раз в 1 час.")
    markup.add(item2)
    item3=types.KeyboardButton("Прошу напоминать об учебе мне раз в 24 часа.")
    markup.add(item3)
    bot.send_message(message.chat.id,'Как часто напоминать Вам об учебе?',reply_markup=markup)

@bot.message_handler(content_types=['text'])
def message_listener(message):
    if message.chat.type=="private":
        if("Прошу напоминать об учебе мне раз в " in message.text):
            try:
                res=message.text.replace("Прошу напоминать об учебе мне раз в ", "")
                res=res.split(" ")
                time=res[0]
                print("res "+str(message.from_user.id))
                file=open('users.txt', 'w')
                if(res[1][:3:]=="час"):
                    file.write(str(message.from_user.id)+":"+time+":"+"1")
                    print(str(message.from_user.id)+":"+time+":"+"1")
                elif(res[1][:3:]=="мин"):
                    file.write(str(message.from_user.id)+":"+time+":"+"0")
                    print(str(message.from_user.id)+":"+time+":"+"0")
                file.close()
                scheduler_start()
                markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1=types.KeyboardButton("Видеоматериалы")
                markup.add(item1)
                item2=types.KeyboardButton("Дополнительные материалы")
                markup.add(item2)
                bot.send_message(message.chat.id,'Приятной учебы!',reply_markup=markup)
            except:
                pass
        elif(message.text=="Видеоматериалы"):
            bot.send_message(message.from_user.id, prepare_video())
        elif(message.text=="Дополнительные материалы"):
            bot.send_message(message.from_user.id, prepare_dop())
        else:
            pass
try:
    bot.polling(none_stop=True, interval=0)
except KeyboardInterrupt:
    FLAG=False
    sys.exit()