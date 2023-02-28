import pandas as pd
import telebot
from daily_script import YesPlanetScraper
from datetime import datetime

Dict_Theater={
    'איילון':'1025',
    'חיפה':'1070',
    'באר שבע':'1074',
    'ירושלים':'1073',
    'ראשון לציון':'1072',
    'זכרון יעקב':'1075'
}
BOT_TOKEN = '6046364453:AAG1X0yAcaABlBnC_qlwa_XQVPWfiQ4nsek'
TODAY_DATE=datetime.today().strftime('%Y-%m-%d')

bot = telebot.TeleBot(BOT_TOKEN)

# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):
#     bot.reply_to(message,'hiiiii')
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id,"ברוך הבא לבוט הסרטים!!\nלאיזה קולנוע תרצה  ללכת היום?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
   msg=str(message.text).strip()
   if msg in Dict_Theater:
    theater=Dict_Theater[msg]
    with open("theater.txt", "w") as text_file:
     text_file.write(theater)
    df=pd.read_pickle('pkl_files/'+theater+'_'+TODAY_DATE+'_movies.pkl')
    df=df.drop_duplicates()
    df=df.sort_values('imdb_ratings',ascending=False)
    bot.send_message(message.chat.id,'Title || IMDB RATING || Gross Income')
    for index, row in df.iterrows():
     bot.send_message(message.chat.id,str(row['Title'])+'  ||  '+str(row['imdb_ratings'])+'  ||  '+str(row['imdb_gross'])) 
    # bot.send_photo(message.chat.id, photo=open('table_mpl.png', 'rb')) 
   else:
    if message.reply_to_message:
       f = open("theater.txt", "r")
       theater=f.read() 
       chosen_movie=message.reply_to_message.text.split('|',1)[0].strip()
       df_t=pd.read_pickle('pkl_files/'+theater+'_'+TODAY_DATE+'_times.pkl')
       df_t=df_t.drop_duplicates()
       df_chosen=df_t.loc[df_t['Title']==chosen_movie]
       for index, row in df_chosen.iterrows():
        bot.send_message(message.chat.id,str(row['Type'])+' '+str(row['Time']))         
    else:       
     bot.send_message(message.chat.id,"לא נמצא קולנוע במיקום המבוקש,נסה שוב")   
bot.infinity_polling()