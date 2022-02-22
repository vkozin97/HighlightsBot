import telebot
from telebot import custom_filters
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
#from telebot.handler_backends import State, StatesGroup
#from telebot.storage import StatePickleStorage
from video import cut_and_save_subclip
from dbkeeper import DBKeeper, UserStates
from file_structure import load_structure
import os.path as pth


test_mode = True


token_file = pth.join('Data', 'tg_token.txt')
test_token_file = pth.join('Data', 'tg_test_token.txt')

def get_token(test_mode=True):
    if test_mode:
        filename = test_token_file
    else:
        filename = token_file
        
    with open(filename) as f:
        token = f.read()
    return token


bot = telebot.TeleBot(get_token(test_mode=test_mode))
print('Made bot')
db = DBKeeper(test_mode=test_mode)
print('Connected to DB')
        
        
@bot.message_handler(content_types=['text'])
def master_msg_handler(message):
    user_id = message.from_user.id
    text = message.text
    user_state = db.get_user_state(user_id)
    
    if user_state is None or text.startswith('/start'):
        start(message)
        return
    
    user_state = db.get_user_state(user_id)
    
    if user_state == UserStates.main_menu:
        if text.startswith('/help'):
            help_main_menu(message.chat.id, message.from_user.id)
        elif text.startswith('/change_nickname'):
            db.set_user_state(user_id, UserStates.getting_aquainted)
            get_aquainted(message)
        elif text.startswith('/show_players'):
            show_players(message)
        elif text.startswith('/watch_big_videos'):
            db.set_user_state(user_id, UserStates.choosing_video_to_label)
            choose_video(message.chat.id, user_id)
        elif text.startswith('/watch_highlights'):
            show_my_highlights(message)
        else:
            bot.send_message(message.chat.id, 'Ваш запрос неясен. Посмотрите /help')
    if user_state == UserStates.choosing_video_to_label:
        if text.startswith('/help'):
            help_choose_menu(message)


def get_aquainted(message):
    bot.send_message(message.chat.id, 'Пожалуйста, представьтесь именем, по которому все поймут, что это именно Вы. Например, "ПетяЦБ". Чем короче, тем лучше!')
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
        if len(players_with_this_nickname) > 0 and players_with_this_nickname[0].user_id != message.from_user.id:
            bot.send_message(message.chat.id, 'Такое имя уже занято кем-то другим. Попробуй придумать другое')
            bot.register_next_step_handler(message, get_nickname_again)
        else:
            db.change_player_nickname(message.from_user.id, message.from_user.username, nickname)
            db.set_user_state(message.from_user.id, UserStates.main_menu)
            greeting(message, nickname)
            
def greeting(message, nickname):
    bot.send_message(message.chat.id, 'Привет, ' + nickname + '!')
    help_main_menu(message.chat.id, message.from_user.id)
     
        
def start(message):
    user_id = message.from_user.id
    print(type(user_id), user_id)
    players_with_this_user_id = db.get_players_with_user_id(user_id)
    if len(players_with_this_user_id) == 0:
        db.add_player(message.from_user.id, message.from_user.username, 'Игрок')
        db.set_user_state(message.from_user.id, UserStates.getting_aquainted)
        bot.send_message(message.chat.id, 'Привет!')
        bot.send_message(message.chat.id, 'Меня зовут Хайлайт-бот')
        bot.send_message(message.chat.id, 'А Вас?')
        get_aquainted(message)
    else:
        db.set_user_state(message.from_user.id, UserStates.main_menu)
        greeting(message, players_with_this_user_id[0].nickname)            


def help_main_menu(chat_id, user_id):
    bot.send_message(chat_id,
                     'Вы в главном меню. Список доступных команд:\n'
                     ' - /help - показать список команд, доступных в текущем меню\n'
                     ' - /change_nickname - выбрать себе другое имя\n'
                     ' - /show_players - показать список всех игроков\n'
                     ' - /watch_big_videos - смотреть видео\n'
                     ' - /watch_highlights - смотреть хайлайты')
                    

def help_choose_menu(message):
    current_video_path = db.get_user_current_video(message.from_user.id)
    add_text = f'\nСейчас выбрана папка {current_video_path}.' if current_video_path != '' else ''
    bot.send_message(message.chat.id,
                     'Вы в меню выбора видео.\n' + add_text + \
                     'Список доступных команд:\n'
                     '\n\n - /help - показать список команд, доступных в текущем меню')

def help_in_labeling(message):
    current_video_path = db.get_user_current_video(message.user.id)
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
        txt = 'Список игроков:\n'
        for player in players:
            txt += f'- <a href="tg://user?id={player.user_id}">{player.nickname}</a>' + '\n'
            
        bot.send_message(message.chat.id, txt, parse_mode='HTML')
        
    
def _get_current_position_in_structure(user_id):
    current_video_path = db.get_user_current_video(user_id)
    video_path_split = current_video_path.split('/')
    file_structure = load_structure()
    cur_position_in_structure = file_structure
    
    all_found = True
    for folder_name in video_path_split:
        found = False
        for folder_in_structure in cur_position_in_structure['folders']:
            if folder_in_structure['name'] == folder_name:
                found = True
                cur_position_in_structure = folder_in_structure['dir_content']
                break
        if not found:
            all_found = False
            break
        
    if not all_found:
        cur_position_in_structure = file_structure
        db.set_user_current_video(user_id, '')
        
    return cur_position_in_structure
    

def choose_video(chat_id, user_id):
    cur_position = _get_current_position_in_structure(user_id)
    current_video_path = db.get_user_current_video(user_id)
    
    keyboard = InlineKeyboardMarkup()
    for folder in cur_position['folders']:
        keyboard.add(InlineKeyboardButton(text=folder['name'], callback_data='fldr' + folder['name']))
    for file in cur_position['files']:
        keyboard.add(InlineKeyboardButton(text=file['name'], callback_data='file' + file['name']))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='%%% Назад %%%'))
    
    if len(cur_position['folders']) > 0:
        if len(cur_position['files']) > 0:
            msg_text = 'Выберите папку/видео:'
        else:
            msg_text = 'Выберите папку:'
    else:
        if len(cur_position['files']) > 0:
            msg_text = 'Выберите видео:'
        else:
            msg_text = 'Папка пуста'
            
    bot.send_message(chat_id, msg_text, reply_markup=keyboard)
    # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mainmenu)


def notify_structure_is_old_and_choose_again(chat_id, user_id):
    bot.send_message(chat_id, 'Структура файлов поменялась, пока Вы выбирали видео. Нужно начать снова.')
    db.set_user_current_video(user_id, '')
    choose_video(chat_id, user_id)  


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    cur_position = _get_current_position_in_structure(user_id)
    current_video_path = db.get_user_current_video(user_id)
    split = current_video_path.split('/')
    
    chosen_text = ''
    if call.data == '%%% Назад %%%':
        chosen_text = 'Назад'
        bot.edit_message_text(f'Выбрано: {chosen_text}', chat_id, call.message.message_id)
        if len(current_video_path) == 0:
            db.set_user_state(user_id, UserStates.main_menu)
            help_main_menu(chat_id, user_id)
        else:
            db.set_user_current_video(user_id, '/'.join(split[:-1]))
            choose_video(chat_id, user_id)
    else:
        fldr_or_file, name = call.data[:4], call.data[4:]
        db.set_user_current_video(user_id, (current_video_path + '/' + name).lstrip('/'))
        chosen_text = name
        bot.edit_message_text(f'Выбрано: {chosen_text}', chat_id, call.message.message_id)
        if fldr_or_file == 'fldr':
            choose_video(chat_id, user_id)
        else:
            url = None
            for file in cur_position['files']:
                if file['name'] == name:
                    url = file['public_url']
                    break
            if url is None:
                notify_structure_is_old_and_choose_again(chat_id, user_id)
            else:
                bot.send_message(chat_id, f'Вы выбрали видео: <a href=\'{url}\'>{db.get_user_current_video(user_id)}</a>. Нажмите на ссылку, чтобы посмотреть видео.', parse_mode='HTML')
                bot.send_message(chat_id, 'Скоро здесь появится возможность отмечать хайлайты на выбранном видео. А пока приятного просмотра! Отправляю Вас в главное меню')
                db.set_user_state(user_id, UserStates.main_menu)
                help_main_menu(chat_id, user_id)


def show_my_highlights(message):
    bot.send_message(message.chat.id, 'Скоро я научусь этой функции!')
    help_main_menu(message.chat.id, message.from_user.id)

    
bot.infinity_polling()