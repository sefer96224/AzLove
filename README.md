import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

# 🔹 BURADA ÖZ YENİ TOKENİNİ YAZ
telegram_api_key = '7789510105:AAEvk0cUuMbkHD6FLnmDp_9P-IUE4L3rX7k'

bot = telebot.TeleBot(telegram_api_key)

# 🔹 SQLite baza
conn = sqlite3.connect('userdata.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    city TEXT,
    gender TEXT,
    interests TEXT,
    photo TEXT,
    liked_users TEXT
)
''')

conn.commit()

# 🔹 RAM-da saxladığımız müvəqqəti məlumatlar
user_data = {}


def save_user_data(user_id, data):
    with sqlite3.connect('userdata.db') as conn:
        c = conn.cursor()
        liked_users = ','.join(map(str, data.get('liked_users', [])))
        c.execute('''
        INSERT OR REPLACE INTO users (chat_id, name, age, city, gender, interests, photo, liked_users)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['name'],
            data['age'],
            data['city'],
            data['gender'],
            data.get('interests', ''),
            data.get('photo', ''),
            liked_users
        ))
        conn.commit()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {
        'name': None,
        'age': None,
        'city': None,
        'gender': None,
        'interests': None,
        'photo': None,
        'liked_users': [],
        'viewed_profiles': []
    }

    bot.send_message(
        message.chat.id,
        'Mən sənə öz sevgini və ya dost tapmağına kömək edəcəm. Olar bir neçə sual verim?'
    )

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton('Başlayaq! 🚀')
    markup.add(button1)

    bot.send_message(message.chat.id, "Zəhmət olmasa düyməni basın:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Başlayaq! 🚀')
def handle_start(message):
    bot.send_message(message.chat.id, 'Sənə necə müraciət edək? Adını de☺️')


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]['name'] is None)
def get_name(message):
    user_data[message.chat.id]['name'] = message.text.strip()
    bot.send_message(message.chat.id, 'Neçə yaşın var?')


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]['age'] is None)
def get_age(message):
    if message.text.isdigit():
        age = int(message.text)
        if age < 18:
            bot.send_message(message.chat.id, 'Bu xidmət yalnız 18 yaşdan yuxarı şəxslər üçündür.')
            user_data.pop(message.chat.id, None)
        else:
            user_data[message.chat.id]['age'] = age
            bot.send_message(message.chat.id, 'Hansı şəhərdə yaşayırsan?')
    else:
        bot.send_message(message.chat.id, 'Zəhmət olmasa yaşını rəqəmlərlə yaz.')


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]['city'] is None)
def get_city(message):
    user_data[message.chat.id]['city'] = message.text.strip()
    bot.send_message(message.chat.id, 'Cinsiyyətini öyrənək 😊')

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_male = KeyboardButton('Kişi')
    button_female = KeyboardButton('Qadın')
    markup.add(button_male, button_female)

    bot.send_message(message.chat.id, 'Zəhmət olmasa cinsiyyətini seç:', reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.chat.id in user_data
    and user_data[message.chat.id]['gender'] is None
    and message.text in ['Kişi', 'Qadın']
)
def handle_gender(message):
    user_data[message.chat.id]['gender'] = message.text
    bot.send_message(message.chat.id, 'Özün və maraqların haqqında danış.')


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]['interests'] is None)
def get_interests(message):
    user_data[message.chat.id]['interests'] = message.text
    bot.send_message(message.chat.id, 'İndi mənə bir şəkil göndər.')


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Əgər /start eləməyibsə, ignore edək
    if message.chat.id not in user_data:
        return

    user_data[message.chat.id]['photo'] = message.photo[-1].file_id
    save_user_data(message.chat.id, user_data[message.chat.id])
    bot.send_message(message.chat.id, 'Anketiniz hazırdır! İndi sənə uyğun profilləri göstərim 💘')
    send_profiles_to_user(message.chat.id)


def send_profiles_to_user(user_id):
    with sqlite3.connect('userdata.db') as conn:
        c = conn.cursor()

        # Öz genderini götür
        c.execute('SELECT gender FROM users WHERE chat_id = ?', (user_id,))
        result = c.fetchone()
        if not result:
            bot.send_message(user_id, 'Sistemdə profiliniz tapılmadı.')
            return

        user_gender = result[0]
        target_gender = 'Qadın' if user_gender == 'Kişi' else 'Kişi'

        c.execute('SELECT * FROM users WHERE chat_id != ? AND gender = ?', (user_id, target_gender))
        all_users = c.fetchall()

        viewed_profiles = user_data[user_id].get('viewed_profiles', [])
        new_profiles = [user for user in all_users if user[0] not in viewed_profiles]

        if new_profiles:
            user = new_profiles[0]
            user_data[user_id]['viewed_profiles'].append(user[0])

            info = f"{user[1]}, {user[2]} yaş, {user[3]}, {user[4]}"
            if user[5]:
                info += f"\nMaraqlar: {user[5]}"

            bot.send_message(user_id, info)
            if user[6]:
                bot.send_photo(user_id, user[6])

            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(KeyboardButton('👍'), KeyboardButton('👎'))
            bot.send_message(user_id, 'Bu profili bəyəndinmi?', reply_markup=markup)

            bot.register_next_step_handler_by_chat_id(user_id, handle_like_dislike, user[0])
        else:
            bot.send_message(user_id, 'Anketləri Bitdi. Daha sonra yenə yoxlaya bilərsən.')


def handle_like_dislike(message, liked_user_id):
    if message.text == '👍':
        user_data[message.chat.id]['liked_users'].append(liked_user_id)
        # 🔹 BƏYƏNDİKDƏ BAZANI YENİLƏ
        save_user_data(message.chat.id, user_data[message.chat.id])
        check_if_mutual_like(message.chat.id, liked_user_id)

    # Növbəti profil
    send_profiles_to_user(message.chat.id)


def check_if_mutual_like(user_id, liked_user_id):
    with sqlite3.connect('userdata.db') as conn:
        c = conn.cursor()
        c.execute('SELECT liked_users FROM users WHERE chat_id = ?', (liked_user_id,))
        result = c.fetchone()

        if result and result[0]:
            liked_users = result[0].split(',')
            if str(user_id) in liked_users:
                bot.send_message(user_id, "🎉 Siz bir-birinizi bəyəndiniz! İndi danışmağa başlaya bilərsiniz.")
                bot.send_message(liked_user_id, "🎉 Siz bir-birinizi bəyəndiniz! İndi danışmağa başlaya bilərsiniz.")
                send_profile_to_user(user_id, liked_user_id)
                send_profile_to_user(liked_user_id, user_id)


def send_profile_to_user(user_id, profile_user_id):
    with sqlite3.connect('userdata.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE chat_id = ?', (profile_user_id,))
        user = c.fetchone()

        if user:
            info = f"{user[1]}, {user[2]} yaş, {user[3]}, {user[4]}"
            if user[5]:
                info += f"\nMaraqlar: {user[5]}"
            bot.send_message(user_id, info)
            if user[6]:
                bot.send_photo(user_id, user[6])


bot.polling(non_stop=True)
