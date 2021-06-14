import telebot
from bs4 import BeautifulSoup
import os
import re
import time
import traceback
import cloudscraper


my_chat_id = 1681990612
requests = cloudscraper.CloudScraper()


with open('v.env') as f:
    API_KEY = f.read().split('API_KEY=')[1].strip()
bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message, "Hey! Hows it going?")


@bot.message_handler(commands=['hello', 'help', 'start'])
def hello(message):
    msg = """Hello! This is Zicky!
I was created by a young and pationate boy named Zubayer.
His ig: https://www.instagram.com/zubayer204/
"""
# His ig: https://www.instagram.com/zubayer204/
    bot.send_message(message.chat.id, msg)
    my_msg = f"{message.chat.first_name} {message.chat.last_name} {message.chat.username}"
    print(my_msg)
    bot.send_message(my_chat_id, my_msg)

    msg = """
Get ready to be amazed! To download your favorite movie just send a message to me like this:

Movie: movie name

For example if you want to download karnan movie, just send this:

Movie: karnan

Then you'll get a list of the search result.
Choose your required movie by number.
Voala! You'll get all the download links.
"""
    bot.send_message(message.chat.id, msg)
    # bot.send_message(message.chat.id, 'Bot Down. We are having some issues cuz it was hosted for FREE')


def check_movie(message):
    request = message.text.split(': ')
    if len(request) < 2 or request[0].lower() not in "movie":
        bot.send_message(message.chat.id, """Please check the spelling or formatting.
The format is:

Movie: movie name""")
        return False
    else:
        return True


@bot.message_handler(func=check_movie)
def get_movie(message):
    
    try:
        
        
        mv_name = message.text.split(': ')[1]
        
        my_msg = f"{message.chat.first_name} {message.chat.last_name} {mv_name}"
        bot.send_message(1681990612, my_msg)

        search_term = mv_name.strip()
        search_term = search_term.replace(' ', '+')
        url = "https://mlwbd.shop/?s=" + search_term

        bot.send_message(message.chat.id, 'Getting Movies list. Please wait...')
        
        try:
            res = requests.get(url)
        except:
            bot.send_message(message.chat.id, 'There\'s been a huge load on this bot. We are sorry from the core of our heart. Please try again later')
            time.sleep(0.1)
            err = traceback.format_exc()
            bot.send_message(my_chat_id, err)
            print(err)
            return 
        soup = BeautifulSoup(res.content, 'lxml')
        results = soup.select(".result-item article")
        if len(results) == 0:
            results = soup.select(".title")
            if len(results) == 0:
                bot.send_message(message.chat.id, 'No results found. Please try again with a different spelling')
                return
        movies = {}

        for idx, result in enumerate(results):
            movies[idx] = result.a['href']
            title = result.find('div', attrs={'class': 'title'}).getText()
            try:
                rating = result.find('span', attrs={'class': 'rating'}).getText()
            except AttributeError:
                rating = 'Not Given'
            try:
                year = result.find('span', attrs={'class': 'year'}).getText()
            except AttributeError:
                year = 'Not Given'
            try:
                desc = result.find('div', attrs={'class': 'contenido'}).getText()
            except AttributeError:
                desc = 'Not Given'
            msg_text = f"""
    No: {idx+1}
    Title: {title}

    Rating: {rating}    Year: {year}
    {desc}
    """
            s_m = bot.send_message(message.chat.id, msg_text)
            time.sleep(0.1)
            msg_id = s_m.message_id
            if idx == 0:
                bot.pin_chat_message(message.chat.id, msg_id)
            if idx == 10:
                break
        msg = bot.send_message(message.chat.id, "Enter the movie No. you wanna download. Just the number, example: 1") # noqa
        bot.register_next_step_handler(msg, get_num, movies)
        
    except:
        bot.send_message(message.chat.id, 'There was an error. Please try again')
        err = traceback.format_exc()
        bot.send_message(my_chat_id, err)
        print(err)


def get_num(message, movies):
    
    try:
        
        
        bot.unpin_all_chat_messages(message.chat.id)
        try:
            movie_num = int(message.text)
        except Exception:
            movie_num = int(re.findall('([1-9][0-9]*)', 'No. 011')[0])
            bot.send_message(message.chat.id, 'Try to give just the number from next time')
            time.sleep(0.1)

        try:
            bot.send_message(message.chat.id, "Getting Download URLs. Please wait...")
            try:
                res = requests.get(movies[movie_num-1])
            except KeyError:
                bot.send_message(message.chat.id, 'Please enter a valid number')
                bot.register_next_step_handler(message, get_num, movies)
                return
            except Exception:
                bot.send_message(message.chat.id, 'There\'s been a huge load on this bot. We are sorry from the core of our heart. Please try again later')
                time.sleep(0.1)
                err = traceback.format_exc()
                bot.send_message(my_chat_id, err)
                print(err)
                return
        except Exception:
            m = bot.send_message(message.chat.id, f'Please enter a number between 1 and {len(movies)}')
            bot.register_next_step_handler(m, get_num, movies)
            return
        soup = BeautifulSoup(res.content, 'lxml')
        try:
            main_url = soup.select("#download")[0].input['value']
        except:
            bot.send_message(message.chat.id, 'No download link found! Please messge to @zubayer204 with the movie you were trying to download')
            err = traceback.format_exc()
            time.sleep(0.1)
            bot.send_message(my_chat_id, err + "\n\n" + movies[movie_num-1])
            print(err)
            return
        img_url = soup.select(".poster img")[0]['src']
        try:
            img_res = requests.get(img_url)
            image = True
            with open('out.jpg', 'wb') as f:
                for chunk in img_res.iter_content(3000):
                    f.write(chunk)
        except:
            image = False
        try:
            res = requests.get(main_url)
        except:
            bot.send_message(message.chat.id, 'There\'s been a huge load on this bot. We are sorry from the core of our heart. Please try again later')
            return
        soup = BeautifulSoup(res.content, 'lxml')
        div = soup.select(".entry-content")
        li = div[0].findAll("li")
        x = True
        if image:
            with open('out.jpg', 'rb') as img:
                bot.send_chat_action(message.chat.id, 'upload_photo')
                bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id) # noqa
        for each in li:
            msg = ""
            text = each.getText()
            pixel = text.split(" : ")[0]
            msg += pixel + "\n"
            for a in each.findAll('a'):
                msg += '\n' + a.getText() + ": " + a['href']
            bot.send_message(message.chat.id, msg)
            x = False
        if len(li) == 0:
            p = div[0].findAll('p', attrs={'style': 'text-align: center;'})
            for i in range(0, len(p), 2):
                msg = p[i].getText() + "\n"
                try:
                    for a in p[i+1].findAll('a'):
                        msg += '\n' + a.getText() + ": " + a['href'] + '\n'
                except IndexError:
                    msg = ''
                    for a in p[i].findAll('a'):
                        msg += '\n' + a.getText() + ": " + a['href'] + '\n'
                bot.send_message(message.chat.id, msg)
                x = False
        if x:
            a = div[0].findAll('a')
            for each in a:
                msg = "\n" + each.getText() + ": " + each['href'] + '\n'
                bot.send_message(message.chat.id, msg)

        bot.send_message(message.chat.id, 'Thanks for using my service. If there is any problem, kindly contact me in tg: @zubayer204')


    except:
        bot.send_message(message.chat.id, 'There was an error. Please try again')
        err = traceback.format_exc()
        bot.send_message(my_chat_id, err)
        print(err)
# @bot.message_handler()
# def err(message):
#     bot.send_message(message.chat.id, "BOT is currently down. It happened because it was hosted for free.")


bot.polling()
