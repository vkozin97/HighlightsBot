import telebot
from telebot import custom_filters
#from telebot.handler_backends import State, StatesGroup
#from telebot.storage import StatePickleStorage
from video import cut_and_save_subclip
from dbkeeper import DBKeeper, UserStates
import os.path as pth


token_file = pth.join('Data', 'tg_token.txt')

def get_token(filename=token_file):
    with open(filename) as f:
        token = f.read()
    return token


#state_storage = StatePickleStorage('Data/states.pkl')
bot = telebot.TeleBot(get_token())
print('Made bot')
db = DBKeeper()
print('Connected to DB')
        
        
@bot.message_handler(content_types=['text'])
def master_msg_handler(message):
    print('master_msg_handler was called')
    user_id = message.from_user.id
    text = message.text
    
    if text.startswith('/start'):
        start(message)
        return
    
    user_state = db.get_user_state(user_id)
    print(user_state.name)
    
    if user_state == UserStates.main_menu:
        if text.startswith('/help'):
            help_main_menu(message)
        elif text.startswith('/change_nickname'):
            db.set_user_state(user_id, UserStates.getting_aquainted)
            get_aquainted(message)
        elif text.startswith('/show_players'):
            show_players(message)
        elif text.startswith('/register_highlights'):
            db.set_user_state(user_id, UserStates.choosing_video_to_label)
            choose_video(message)
        elif text.startswith('/show_highlights'):
            show_my_highlights(message)
        else:
            bot.send_message(message.chat.id, 'Ваш запрос неясен. Посмотрите /help')


def get_aquainted(message):
    bot.send_message(message.chat.id, 'Пожалуйста, представься именем, по которому все поймут, что это именно ты. Например, "ПетяЦБ". Чем короче, тем лучше!')
    bot.send_message(message.chat.id, 'В ИМЕНИ НЕ ДОЛЖНО БЫТЬ ПРОБЕЛОВ!')
    bot.register_next_step_handler(message, get_nickname)

def get_nickname_again(message):
    get_nickname(message)

def get_nickname(message):
    nickname = message.text
    if ' ' in nickname:
        bot.send_message(message.chat.id, 'В имени не должно быть пробелов. Попробуй придумать другое')
        bot.register_next_step_handler(message, get_nickname_again)
        
    elif '%' in nickname:
        bot.send_message(message.chat.id, 'В имени не должно быть знака "%". Попробуй придумать другое')
        bot.register_next_step_handler(message, get_nickname_again)
    
    else:
        players_with_this_nickname = db.get_players_with_nickname(nickname)
        if len(players_with_this_nickname) > 0 and players_with_this_nickname[0][1] != message.from_user.id:
            bot.send_message(message.chat.id, 'Такое имя уже занято кем-то другим. Попробуй придумать другое')
            bot.register_next_step_handler(message, get_nickname_again)
        else:
            db.change_player_nickname(message.from_user.id, message.from_user.username, nickname)
            db.set_user_state(message.from_user.id, UserStates.main_menu)
            greeting(message, nickname)
            
def greeting(message, nickname):
    bot.send_message(message.chat.id, 'Привет, ' + nickname + '!')
    bot.send_message(message.chat.id, 'Вот, что я умею:')
    help_main_menu(message)
     
        
def start(message):
    user_id = message.from_user.id
    print(type(user_id), user_id)
    players_with_this_user_id = db.get_players_with_user_id(user_id)
    if len(players_with_this_user_id) == 0:
        db.add_player(message.from_user.id, message.from_user.username, None)
        db.set_user_state(message.from_user.id, UserStates.getting_aquainted)
        bot.send_message(message.chat.id, 'Привет!')
        bot.send_message(message.chat.id, 'Меня зовут Хайлайт-бот')
        bot.send_message(message.chat.id, 'А как тебя зовут?')
        get_aquainted(message)
    else:
        db.set_user_state(message.from_user.id, UserStates.main_menu)
        greeting(message, players_with_this_user_id[0][3])            


def help_main_menu(message):
    bot.send_message(message.chat.id,
                         '''\
/help - выдать список команд
/change_nickname - выбрать себе другое имя
/show_players - показать всех игроков
/register_highlights - погнали искать хайлайты!
/show_highlights - смотреть хайлайты, которые мы совместно нашли\
                        ''')
                    

def help_in_labeling(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        current_video_path = data['current_video_path']
    bot.send_message(message.chat.id,
                    'В данный момент вы размечаете таймкоды для видео:\n'
                    f'{current_video_path}\n'
                    'Введите таймкод с интересным моментом на этом видео. Например, напишите мне "1:23"'
                    )
                    
                
def change_nickname(message):
    get_aquainted(message)
    

def show_players(message):
    players = db.get_players()
    if len(players) == 0:
        bot.send_message(message.chat.id, 'Список игроков пока пуст')
    else:
        txt = ''
        for _, user_id, username, nickname, user_state_num in players:
            txt += nickname + (f' (@{username})' if username is not None else '') + '\n'
            
        bot.send_message(message.chat.id, txt)
        
    
def choose_video(message):
    bot.send_message(message.chat.id, f'Вы вошли в режим выбора видео для разметки. Он пока не реализован, перенаправляю вас обратно в меню.')
    db.set_user_state(message.from_user.id, UserStates.main_menu)
    help_main_menu(message)


def show_my_highlights(message):
    bot.send_message(message.chat.id, 'Скоро я научусь этой функции!')

    
bot.infinity_polling()